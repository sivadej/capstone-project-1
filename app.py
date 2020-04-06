from flask import Flask, redirect, session, url_for, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User
from flask_login import LoginManager, current_user
from os import environ

# IMPORT AND REGISTER BLUEPRINTS

from api.api_requests import get_data, get_movie_detail
from bp_movie.movie import bp_movie
from bp_search.search import bp_search
from bp_users.users import bp_users
from bp_watchlists.watchlists import bp_watchlists

app = Flask(__name__)

app.register_blueprint(bp_users)
app.register_blueprint(bp_search)
app.register_blueprint(bp_watchlists)
app.register_blueprint(bp_movie)

# use local development config vars if folder exists, otherwise use environment vars
# '/config' folder should never be tracked in source control!
import importlib
dev_config = importlib.util.find_spec('config')
if dev_config is not None:
    from config.app_config import DB_URI, SECRET_KEY
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
else:
    DB_URI = environ.get('DATABASE_URL')
    SECRET_KEY = environ.get('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = SECRET_KEY
debug = DebugToolbarExtension(app)

connect_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/', methods=['GET','POST'])
def redirect_to_search():
    return redirect(url_for('bp_search.show_search'))