from flask import Blueprint, render_template

bp_movie = Blueprint('bp_movie', __name__,
    template_folder='templates',
    static_folder='static')

@bp_movie.route('/getmovies')
def getmovies():
	return('hello from movie blueprint')