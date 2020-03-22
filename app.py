from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Watchlist, Movie, Watchlist_Movie
from api_requests import get_data
from forms import MovieSearchForm
from app_config import DB_URI, SECRET_KEY
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def show_home():
    return redirect('/search')

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

@app.route('/watchlist/<int:watchlist_id>/add-movie/<int:unogs_id>', methods=['POST'])
def add_movie_to_watchlist(watchlist_id, unogs_id):
    new_entry = Watchlist_Movie(watchlist_id=watchlist_id, movie_id=get_dbmovie_id(unogs_id))
    try:
        db.session.add(new_entry)
        db.session.commit()
    except:
        return('error')
    return('added to watchlist!')

@app.route('/watchlist/<int:id>')
def show_watchlist_detail(id):
    watchlist = Watchlist.query.get_or_404(id)
    return render_template('watchlist_detail.html', watchlist=watchlist)

################### USER ROUTES #######################

@app.route('/logout')
def user_logout():
    pass

@app.route('/login')
def user_logout():
    pass

################### HELPERS #######################

@app.route('/movie/<int:id>')
def show_movie_details(id):
    movie = Movie.query.get(id)
    return render_template('movie_details.html', movie=movie)

def get_dbmovie_id(unogs_id):
    dbmovie = Movie.query.filter(Movie.unogs_id == unogs_id).first_or_404()
    return dbmovie.id