from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String, nullable=False)

    watchlists = db.relationship('Watchlist', backref='user')

    @classmethod
    def register(cls, username, email, password):
        hashed_pass = bcrypt.generate_password_hash(password).decode('UTF-8')
        user = User(
            username = username,
            email = email,
            password = hashed_pass,
            )
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False

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
    title = db.Column(db.String(100), nullable=False)
    video_type = db.Column(db.String(8), nullable=False)

class Watchlist_Movie(db.Model):
    __tablename__ = 'watchlists_movies'

    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlists.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('saved_movies.id'), primary_key=True)