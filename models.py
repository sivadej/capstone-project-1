from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    watchlists = db.relationship('Watchlist', backref='user')

class Watchlist(db.Model):
    __tablename__ = 'watchlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    is_shared = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    movies = db.relationship('SavedMovie', secondary='watchlists_movies')

class SavedMovie(db.Model):
    __tablename__ = 'saved_movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    netflix_id = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(50), nullable=False)
    video_type = db.Column(db.String(8), nullable=False)

class Watchlist_Movie(db.Model):
    __tablename__ = 'watchlists_movies'

    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlists.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('saved_movies.id'), primary_key=True)