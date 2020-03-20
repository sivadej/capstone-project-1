from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension

#from forms import FormClassNamesHere
from models import db, connect_db, User, Watchlist, Movie, Watchlist_Movie
#from api_requests import get_data
from file_to_dict import get_movies_dict

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///what2watch'
app.config['SECRET_KEY'] = 'verysecretindeed'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def show_home():
    return ('hello')

@app.route('/search', methods=['GET'])
def show_search():
    return render_template('search_form.html')

@app.route('/search', methods=['POST'])
def do_search():
    data = get_movies_dict()
    movies = data['results']
    total = data['total']
    return render_template('search_results.html', movies=movies, total=total)