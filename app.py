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
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = True

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