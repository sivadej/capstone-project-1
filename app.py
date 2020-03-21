from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension

#from forms import FormClassNamesHere
from models import db, connect_db, User, Watchlist, Movie, Watchlist_Movie
from api_requests import get_data, save_to_db
from file_to_dict import get_movies_dict, serialize_movies
from forms import MovieSearchForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///what2watch'
app.config['SECRET_KEY'] = 'verysecretindeed'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def show_home():
    return ('hello')

@app.route('/search', methods=['GET', 'POST'])
def show_search():
    form = MovieSearchForm()
    if form.validate_on_submit():
        response = get_data(lang1=form.lang1.data, lang2=form.lang2.data)
        response2 = get_data(lang1=form.lang2.data, lang2=form.lang1.data)
        data = serialize_movies(response)
        data2 = serialize_movies(response2)
        save_to_db(data['results'])
        save_to_db(data2['results'])
        return render_template('search_results.html', movies=data['results'], total=data['total'], movies2=data2['results'], total2=data2['total'])
    else:
        return render_template('search_form.html', form=form)

@app.route('/search-DONOTUSE', methods=['POST'])
def get_search_result():

    data = serialize_movies(get_data())
    movies = data['results']
    total = data['total']

    return render_template('search_results.html', movies=movies, total=total)

@app.route('/search-sample', methods=['POST'])
def show_sample_data():
    data = get_movies_dict()
    movies = data['results']
    total = data['total']
    save_to_db(movies)
    return render_template('search_results.html', movies=movies, total=total)

# route handles unogs id, handles dbmovie, redirect to movie detail by dbmovie id

@app.route('/search-movie/<int:unogs_id>')
def get_movie_from_unogs_id(unogs_id):
    movie = get_dbmovie(unogs_id)
    if movie is None:
        #movie doesn't exist in db yet, so perform api call from netflix id?
        print('movie not found, adding to db')
    return redirect(f'/movie/{movie.id}/details')

@app.route('/movie/<int:id>/details')
def show_movie_details(id):
    movie = Movie.query.get(id)
    return render_template('movie_details.html', movie=movie)

def get_dbmovie(unogs_id):
    dbmovie = Movie.query.filter(Movie.unogs_id == unogs_id).one_or_none()
    if dbmovie is None:
        return None
    return dbmovie