from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from api_requests import get_data, get_movie_detail
from forms import MovieSearchForm, LoginForm, RegisterForm, NewWatchlistForm
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

@app.route('/')
def show_home():
    print(current_user)
    return render_template('hello.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data,
            password = form.password.data,
        )
        login_user(user, remember=form.remember.data)
        return redirect('/')
    return render_template('login.html', form=form)

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
            return render_template('register.html', form=form)
        login_user(user)
        return redirect('/')
    else:
        return render_template('register.html', form=form)






@app.route('/profile', methods=['GET'])
@login_required
def user_profile():
    return render_template('profile.html')

@app.route('/secret')
@login_required
def secret_page():
    return 'this is a secret page'

@app.route('/secret1')
@login_required
def secret_page1():
    if current_user.id == 1:
        return 'you made it to secret page for user 1 ONLY'
    else:
        return 'secret, but not for you dummy'


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
        return render_template('search_form.html', form=form)

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
        'search_results.html',
        movies=movies['results'],
        total=session['total'],
        audio=session['audio'],
        subs=session['subs'],
        next_page=(page_num+1),
        result_start=(((page_num-1)*12)+1),
        result_end=(page_num*12),
        )

################### WATCHLIST ROUTES ###################

@app.route('/watchlist/<int:list_id>/add', methods=['POST'])
def add_movie_to_watchlist(list_id):
    netflix_id = request.form['netflix-id']
    title = request.form['title']
    video_type = request.form['video-type']

    # check if movie exists in db. if not, add it and set dbmovie to new entry reference
    dbmovie = SavedMovie.query.filter(SavedMovie.netflix_id == netflix_id).first()
    if dbmovie is None:
        new_movie = SavedMovie(netflix_id=netflix_id,title=title,video_type=video_type)
        db.session.add(new_movie)
        db.session.commit()
        dbmovie = new_movie

    # retrieve newly returned saved_movie.id and add entry to watchlist_movie.id
    watchlist_entry = Watchlist_Movie(watchlist_id=list_id, movie_id=dbmovie.id)
    
    try:
        db.session.add(watchlist_entry)
        db.session.commit()
    except:
        db.session.rollback()
        return render_template('temp_watchlist_error.html')

    #import pdb;pdb.set_trace()
    return render_template('temp_watchlist_add_success.html')

    # TODO: restrict this action to logged in userid

@app.route('/watchlist/<int:id>')
def show_watchlist_detail(id):
    watchlist = Watchlist.query.get_or_404(id)
    return render_template('watchlist_detail.html', watchlist=watchlist)

@app.route('/watchlist/new', methods=['GET','POST'])
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
        return redirect(f'/watchlist/{watchlist.id}')
    else:
        return render_template('watchlist_new.html', form=form)

@app.route('/watchlists')
def shared_watchlists():
    watchlists = Watchlist.query.filter_by(is_shared=True).all()
    return render_template('watchlists.html', watchlists=watchlists)

@app.route('/user/<int:user_id>/watchlists')
@login_required
def user_watchlists(user_id):
    if current_user.id == user_id:
        watchlists = Watchlist.query.filter_by(user_id=user_id).all()
        return render_template('user_watchlists.html', watchlists=watchlists)
    else:
        return('not authorized to view this user watchlists')


################### MOVIE ROUTES #######################

@app.route('/movie/<int:id>')
def show_movie_details(id):
    dbmovie = SavedMovie.query.get(id)
    movie = get_movie_detail(dbmovie.netflix_id)

    return render_template('movie_details.html', movie=movie)

################### HELPERS #######################

def get_dbmovie_id(netflix_id):
    dbmovie = SavedMovie.query.filter(SavedMovie.netflix_id == netflix_id).first_or_404()
    return dbmovie.id