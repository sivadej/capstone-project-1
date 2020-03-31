from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from api_requests import get_data, get_movie_detail
from forms import MovieSearchForm, LoginForm, RegisterForm, NewWatchlistForm, EditWatchlistForm, EditUserForm, PickWatchlistForMovieForm
from app_config import DB_URI, SECRET_KEY
from sqlalchemy.exc import IntegrityError
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

################### USER AUTH ###################

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/', methods=['GET','POST'])
def redirect_to_search():
    return redirect(url_for('show_search'))

@app.route('/flashme')
def flashme():
    flash('redirected to search','warning')
    return redirect('/')

@app.route('/temp/search', methods=['GET','POST'])
def temp_search():
    form = MovieSearchForm()
    if form.validate_on_submit():
        # save form data to session, send to results page 1
        # TODO: use session data for loading search page values from last visit
        session['audio'] = form.audio.data
        session['subs'] = form.subs.data
        session['start_year'] = form.year_from.data
        session['end_year'] = form.year_to.data
        session['filter_movie'] = form.filter_movie.data
        session['filter_series'] = form.filter_series.data

        try:
            data = json.loads(response)
            movies = data['results']
            total = data['total']
        except:
            movies = None
        return redirect('/search/results/1')

    else:
        if 'total' in session:
            session.pop('total')
        return render_template('temp/temp_search.html', form=form)
    return render_template('temp/temp_search.html')

#@app.route('/')
#def show_home():
#    print(current_user)
#    return render_template('hello.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.','info')
    return redirect('/')

@app.route('/my_lists')
@login_required
def redirect_to_user_watchlists():
    return redirect(f'/user/{current_user.id}/watchlists')


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data,
            password = form.password.data,
        )
        login_user(user, remember=form.remember.data)
        flash('Successfully logged in. Welcome back!','success')
        return redirect('/profile')
    #if form.is_submitted():
    #    flash('Error logging in.','warning')
    return render_template('user/login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data,
            )
            db.session.commit()
        except IntegrityError:
            flash('username taken')
            return render_template('user/register.html', form=form)
        login_user(user)
        return redirect('/')
    else:
        return render_template('user/register.html', form=form)

@app.route('/profile', methods=['GET'])
@login_required
def user_profile():
    return render_template('user/profile.html')

@app.route('/user/<int:user_id>/edit', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    if current_user.id == user_id:
        form = EditUserForm(obj=current_user)
        if form.validate_on_submit():
            user = User.query.get(user_id)
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()     
            return redirect('/profile')

        return render_template('user/edit.html', user=current_user, form=form)
    else:
        return('unauthorized')


################### SEARCH ROUTES ###################

@app.route('/search', methods=['GET', 'POST'])
def show_search():
    form = MovieSearchForm()
    if form.validate_on_submit():
        # save form data to session, send to results page 1
        # TODO: use session data for loading search page values from last visit
        session['audio'] = form.audio.data
        session['subs'] = form.subs.data
        session['start_year'] = form.year_from.data
        session['end_year'] = form.year_to.data
        session['filter_movie'] = form.filter_movie.data
        session['filter_series'] = form.filter_series.data

        try:
            data = json.loads(response)
            movies = data['results']
            total = data['total']
        except:
            movies = None
        return redirect('/search/results/1')

    else:
        if 'total' in session:
            session.pop('total')
        return render_template('newindex.html', form=form)

@app.route('/search/results/<int:page_num>')
def get_next_search_page(page_num):
    response = get_data(
            audio = session['audio'],
            subs = session['subs'],
            start_year = session['start_year'],
            end_year = session['end_year'],
            filter_movie = session['filter_movie'],
            filter_series = session['filter_series'],
            offset = ((page_num-1)*12),
            )
    movies = json.loads(response)
    # store total results found because it is only returned by API when offset == 0
    if page_num == 1:
        session['total'] = movies['total']

    return render_template(
        'search/search_results.html',
        movies=movies['results'],
        total=session['total'],
        audio=session['audio'],
        subs=session['subs'],
        page=page_num,
        next_page=(page_num+1),
        result_start=(((page_num-1)*12)+1),
        result_end=(page_num*12),
        )

################### WATCHLIST ROUTES ###################

@app.route('/watchlists/<int:list_id>/insert_movie')
def add_movie_to_watchlist(list_id):

    # restrict action to logged in user
    if current_user.is_anonymous:
        return('only logged in users can perform this action')
    
    # authorize current user is owner of current watchlist
    curr_list = Watchlist.query.get(list_id)
    if curr_list.user_id != current_user.id:
        return('you are not authorized to edit this watchlist')
    
    # check if movie exists in db. if not, add it and set dbmovie to new entry reference
    dbmovie = SavedMovie.query.filter(SavedMovie.netflix_id == session['netflix_id']).first()
    if dbmovie is None:
        new_movie = SavedMovie(
            netflix_id=session['netflix_id'],
            title=session['title'],
            video_type=session['video_type'],
            )
        db.session.add(new_movie)
        db.session.commit()
        dbmovie = new_movie
    
    # clean up session
    session.pop('netflix_id', None)
    session.pop('title', None)
    session.pop('video_type', None)
    
    # retrieve newly returned saved_movie.id and add entry to watchlist_movie.id
    watchlist_entry = Watchlist_Movie(watchlist_id=list_id, movie_id=dbmovie.id)
    
    try:
        db.session.add(watchlist_entry)
        db.session.commit()
    except:
        db.session.rollback()
        return render_template('temp/temp_watchlist_error.html')
    return_page = session['return_page']
    return redirect(f'/search/results/{return_page}')

######

@app.route('/test_picklist/get_watchlist_for_movie', methods=['GET','POST'])
@login_required
def pick_watchlist():
    form = PickWatchlistForMovieForm()
    choices = db.session.query(Watchlist.id, Watchlist.title).filter_by(user_id=current_user.id).all()
    form.watchlist.choices = choices

    # POST: return selected watchlist_id
    if form.validate_on_submit():
        #return_page = session['return_page']
        return redirect(f'/watchlists/{form.watchlist.data}/insert_movie')

    # GET:
    # return list of user-owned watchlists for dropdown display on template
    session['netflix_id'] = request.form['netflix-id']
    session['title'] = request.form['title']
    session['video_type'] = request.form['video-type']
    session['return_page'] = request.form['return-page']
    return render_template('watchlists/pick_watchlist.html', form=form)


@app.route('/watchlists/<int:list_id>/remove_movie/<int:movie_id>', methods=['POST'])
def remove_movie_from_watchlist(list_id, movie_id):

    # restrict action to logged in user
    if current_user.is_anonymous:
        return('only logged in users can perform this action')
    
    # authorize current user is owner of current watchlist
    curr_list = Watchlist.query.get(list_id)
    if curr_list.user_id != current_user.id:
        return('you are not authorized to edit this watchlist')

    watchlist_entry = Watchlist_Movie.query.filter_by(watchlist_id=list_id, movie_id=movie_id).first()
    db.session.delete(watchlist_entry)
    db.session.commit()
    return redirect(f'/watchlists/{list_id}')

@app.route('/watchlists/<int:list_id>')
def show_watchlist_detail(list_id):
    # list editing options should be displayed for authorized users
    # authorize (check if list owned by current user) and pass boolean into template
    watchlist = Watchlist.query.get_or_404(list_id)

    if current_user.is_authenticated:
        is_owner = True if watchlist.user_id == current_user.id else False
    else:
        is_owner = False

    return render_template('watchlists/watchlist_detail.html', watchlist=watchlist, is_owner=is_owner)

@app.route('/watchlists/new', methods=['GET','POST'])
@login_required
def new_watchlist():
    form = NewWatchlistForm()
    if form.validate_on_submit():
        watchlist = Watchlist(
            title = form.title.data,
            description = form.description.data,
            is_shared = form.is_shared.data,
            user_id = current_user.id
        )
        db.session.add(watchlist)
        db.session.commit()
        return redirect(f'/watchlists/{watchlist.id}')
    else:
        return render_template('watchlists/watchlist_new.html', form=form)

@app.route('/watchlists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_watchlist(list_id):
    watchlist = Watchlist.query.get_or_404(list_id)
    db.session.delete(watchlist)
    db.session.commit()
    return redirect(f'/user/{current_user.id}/watchlists')

@app.route('/watchlists/<int:list_id>/edit', methods=['GET','POST'])
@login_required
def edit_watchlist(list_id):
    watchlist = Watchlist.query.get_or_404(list_id)
    form = EditWatchlistForm(obj=watchlist)
    if form.validate_on_submit():
        watchlist.title = form.title.data
        watchlist.description = form.description.data
        watchlist.is_shared = form.is_shared.data
        db.session.commit()
        return redirect(f'/user/{current_user.id}/watchlists')
    return render_template('watchlists/watchlist_edit.html', form=form)


@app.route('/watchlists')
def shared_watchlists():
    watchlists = Watchlist.query.filter_by(is_shared=True).all()
    return render_template('watchlists/watchlists.html', watchlists=watchlists)

@app.route('/user/<int:user_id>/watchlists')
@login_required
def user_watchlists(user_id):
    if current_user.id == user_id:
        watchlists = Watchlist.query.filter_by(user_id=user_id).all()
        return render_template('user/my_watchlists.html', watchlists=watchlists)
    else:
        return('not authorized to view this user watchlists')
    
@app.route('/user/new')
def redirect_to_register():
    return redirect(url_for('register'))

################### MOVIE ROUTES #######################

@app.route('/movie/<int:id>')
def show_movie_details(id):
    dbmovie = SavedMovie.query.get_or_404(id)
    movie = get_movie_detail(dbmovie.netflix_id)
    return render_template('movie/movie_details.html', movie=movie)

################### HELPERS #######################
