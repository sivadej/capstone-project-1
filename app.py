from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension

#from forms import FormClassNamesHere
from models import db, connect_db, User, Watchlist, Movie, Watchlist_Movie
from api_requests import get_data, save_to_db, single_movie_to_db
from file_to_dict import get_movies_dict, serialize_movies
from forms import MovieSearchForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/what2watch'
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
        #response2 = get_data(lang1=form.lang2.data, lang2=form.lang1.data)
        data = serialize_movies(response)
        movies = data['results']
        save_to_db(movies)
        #data2 = serialize_movies(response2)
        return render_template('search_results.html', movies=movies, total=data['total'])
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
    #import pdb;pdb.set_trace()
    #save_to_db(movies)
    return render_template('search_results.html', movies=movies, total=total)

# route handles unogs id, handles dbmovie, redirect to movie detail by dbmovie id

@app.route('/search-movie/<int:unogs_id>')
def get_movie_from_unogs_id(unogs_id):
    movie = get_dbmovie(unogs_id)
    if movie is None:
        #movie doesn't exist in db yet, so perform api call from netflix id?
        print('movie not found, adding to db')
    return redirect(f'/movie/{movie.id}/details')

@app.route('/movie/<int:id>')
def show_movie_details(id):
    movie = Movie.query.get(id)
    return render_template('movie_details.html', movie=movie)

def get_dbmovie_id(unogs_id):
    dbmovie = Movie.query.filter(Movie.unogs_id == unogs_id).first_or_404()
    return dbmovie.id


#@app.route('/add-to-db/<int:unogs_id>', methods=['POST'])
#def add_to_db(unogs_id):
#    import pdb;pdb.set_trace()
#    movies = g.data['results']
#    single_movie = next((mov for mov in movies['results'] if mov['id']==unogs_id), None)
#    print(single_movie)
#    single_movie_to_db(single_movie)
#    return('added to db!')

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