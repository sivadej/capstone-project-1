from flask import Blueprint, render_template
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from api_requests import get_data, get_movie_detail

bp_movie = Blueprint('bp_movie', __name__,
    template_folder='templates',
    static_folder='static')

@bp_movie.route('/getmovies')
def getmovies():
	return('hello from movie blueprint')

@bp_movie.route('/movie/<int:id>')
def show_movie_details(id):
    dbmovie = SavedMovie.query.get_or_404(id)
    movie = get_movie_detail(dbmovie.netflix_id)
    return render_template('movie/movie_details.html', movie=movie)