from flask import Flask, request, render_template, redirect, flash, session, url_for, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from api_requests import get_data, get_movie_detail
from forms import MovieSearchForm, LoginForm, RegisterForm, NewWatchlistForm, EditWatchlistForm, EditUserForm, PickWatchlistForMovieForm
from sqlalchemy.exc import IntegrityError
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from os import environ

from bp_api.api_requests import bp_api
from bp_movie.movie import bp_movie
from bp_search.search import bp_search
from bp_users.users import bp_users
from bp_watchlists.watchlists import bp_watchlists

app = Flask(__name__)

app.register_blueprint(bp_users)
app.register_blueprint(bp_search)
app.register_blueprint(bp_watchlists)
app.register_blueprint(bp_movie)
app.register_blueprint(bp_api)

# use local development config vars if folder exists, otherwise use environment vars
# '/config' folder should never be tracked in source control!
import importlib
dev_config = importlib.util.find_spec('config')
if dev_config is not None:
    from config.app_config import DB_URI, SECRET_KEY
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
else:
    DB_URI = environ.get('DATABASE_URL')
    SECRET_KEY = environ.get('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = SECRET_KEY
debug = DebugToolbarExtension(app)

connect_db(app)

################### USER AUTH/ROUTES ###################

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/', methods=['GET','POST'])
def redirect_to_search():
    return redirect(url_for('show_search'))

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.','info')
    return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data,
            password = form.password.data,
        )
        if user is False:
            flash('Invalid login details. Try Again.','danger')
            return redirect('/login')
        else:
            login_user(user, remember=form.remember.data)
            flash('Successfully logged in. Welcome back!','success')
            return redirect('/profile')
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
            flash('Username taken.','warning')
            return render_template('user/register.html', form=form)
        login_user(user)
        create_list_for_new_user(user)
        return redirect('/')
    return render_template('user/register.html', form=form)

@login_required
def create_list_for_new_user(user):
    # create a private list for newly registered user
    title = f"{user.username}'s Watchlist"
    new_list = Watchlist(title=title, is_shared=False, user_id=user.id)
    db.session.add(new_list)
    db.session.commit()

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
            flash('Changes successfully made to account','info')
            return redirect('/profile')

        return render_template('user/edit.html', user=current_user, form=form)
    else:
        return('unauthorized')

@app.route('/user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    if current_user.id == user_id:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User account deleted.','warning')
        return redirect('/logout')
    else:
        return('',403)


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
        return render_template('home_search.html', form=form)

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
    # store total results found because it is only available on page 1 of request
    if page_num == 1:
        session['total'] = movies['total']
    
    if session['total'] == 0:
        return render_template('search/search_noresults.html')
    else:
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

@app.route('/pick_watchlist_from_search')
def show_picks():
    # render dropdown of user watchlists. expecting to use for ajax modal, return html template without base
    form = PickWatchlistForMovieForm()
    choices = db.session.query(Watchlist.id, Watchlist.title).filter_by(user_id=current_user.id).all()
    form.watchlist.choices = choices
    return render_template('watchlists/my_watchlists_dropdown.html', form=form)

@app.route('/watchlist_add_from_search', methods=['POST'])
def add_movie_to_watchlist_from_search():
    list_id = int(request.json['watchlistId'])
    netflix_id = int(request.json['nfid'])
    title = request.json['title']
    video_type = request.json['vtype']

    # restrict action to logged in user
    # authorize current user is owner of current watchlist
    curr_list = Watchlist.query.get(list_id)
    if curr_list.user_id != current_user.id or current_user.is_anonymous:
        return('Unauthorized action.',403)

    movie_entry = get_movie_by_nfid(SavedMovie(
            netflix_id=netflix_id,
            title=title,
            video_type=video_type,
            ))

    watchlist_entry = Watchlist_Movie(watchlist_id=list_id, movie_id=movie_entry.id)

    try:
        db.session.add(watchlist_entry)
        db.session.commit()
    except:
        db.session.rollback()
        return ('Movie is already in the selected Watchlist.', 202)

    return ('Added to your Watchlist!', 200)

def get_movie_by_nfid(movie):
    # return instance of SavedMovie from database if exists
    # or create new SavedMovie if needed
    dbmovie = SavedMovie.query.filter(SavedMovie.netflix_id == movie.netflix_id).first()
    if dbmovie is not None:
        return dbmovie
    else:
        db.session.add(movie)
        db.session.commit()
        return movie

@app.route('/watchlists/<int:list_id>/remove_movie/<int:movie_id>', methods=['POST'])
def remove_movie_from_watchlist(list_id, movie_id):

    # restrict action to logged in user
    # authorize current user is owner of current watchlist
    curr_list = Watchlist.query.get(list_id)
    if curr_list.user_id != current_user.id or current_user.is_anonymous:
        return('',403)

    watchlist_entry = Watchlist_Movie.query.filter_by(watchlist_id=list_id, movie_id=movie_id).first()
    movie = SavedMovie.query.get(movie_id)
    title = movie.title
    db.session.delete(watchlist_entry)
    db.session.commit()
    flash(f'Removed "{title}" from list','warning')
    return redirect(f'/watchlists/{list_id}')

@app.route('/watchlists/<int:list_id>')
def show_watchlist_detail(list_id):
    # list editing options should be displayed for authorized users
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
        flash(f'Watchlist "{watchlist.title}" successfully added','info')
        return redirect('/my_lists')
    else:
        return render_template('watchlists/watchlist_new.html', form=form)

@app.route('/watchlists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_watchlist(list_id):
    watchlist = Watchlist.query.get_or_404(list_id)
    title = watchlist.title
    db.session.delete(watchlist)
    db.session.commit()
    flash(f'Watchlist "{title}" deleted','warning')
    return redirect(f'/user/{current_user.id}/watchlists')

@app.route('/watchlists/<int:list_id>/edit', methods=['GET','POST'])
@login_required
def edit_watchlist(list_id):
    watchlist = Watchlist.query.get_or_404(list_id)
    if current_user.id == watchlist.user_id:
        form = EditWatchlistForm(obj=watchlist)
        if form.validate_on_submit():
            watchlist.title = form.title.data
            watchlist.description = form.description.data
            watchlist.is_shared = form.is_shared.data
            db.session.commit()
            flash('Changes successfully made to watchlist','info')
            return redirect(f'/user/{current_user.id}/watchlists')
        return render_template('watchlists/watchlist_edit.html', form=form)
    else:
        return('',403)

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
        return('',403)

@app.route('/my_lists')
@login_required
def redirect_to_user_watchlists():
    return redirect(f'/user/{current_user.id}/watchlists')

################### MOVIE ROUTES #######################

