from flask import Flask, request, render_template, redirect, flash, session, url_for, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from api.api_requests import get_data, get_movie_detail
from forms import MovieSearchForm, LoginForm, RegisterForm, NewWatchlistForm, EditWatchlistForm, EditUserForm, PickWatchlistForMovieForm
from sqlalchemy.exc import IntegrityError
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from os import environ

bp_watchlists = Blueprint('bp_watchlists', __name__,
    template_folder='templates',
    static_folder='static')


################ WATCHLIST HELPER FUNCTIONS #############

def get_movie_by_nfid(movie):
    # return instance of SavedMovie from database if exists
    # or create new SavedMovie if needed
    dbmovie = SavedMovie.query.filter(SavedMovie.netflix_id == movie.netflix_id).first()
    if dbmovie is not None:
        return dbmovie
    else:
        db.session.add(movie)
        db.session.commit()
        return movie

################### WATCHLIST ROUTES ###################

@bp_watchlists.route('/watchlists')
def shared_watchlists():
    watchlists = Watchlist.query.filter_by(is_shared=True).all()
    return render_template('watchlists/watchlists.html', watchlists=watchlists)

@bp_watchlists.route('/pick_watchlist_from_search')
def show_picks():
    # render dropdown of user watchlists. expecting to use for ajax modal, return html template without base
    form = PickWatchlistForMovieForm()
    choices = db.session.query(Watchlist.id, Watchlist.title).filter_by(user_id=current_user.id).all()
    form.watchlist.choices = choices
    return render_template('watchlists/my_watchlists_dropdown.html', form=form)

@bp_watchlists.route('/watchlist_add_from_search', methods=['POST'])
def add_movie_to_watchlist_from_search():
    list_id = int(request.json['watchlistId'])
    netflix_id = int(request.json['nfid'])
    title = request.json['title']
    video_type = request.json['vtype']

    # restrict action to logged in user
    # authorize current user is owner of current watchlist
    curr_list = Watchlist.query.get(list_id)
    if curr_list.user_id != current_user.id or current_user.is_anonymous:
        return('Unauthorized action.',403)

    movie_entry = get_movie_by_nfid(SavedMovie(
            netflix_id=netflix_id,
            title=title,
            video_type=video_type,
            ))

    watchlist_entry = Watchlist_Movie(watchlist_id=list_id, movie_id=movie_entry.id)

    try:
        db.session.add(watchlist_entry)
        db.session.commit()
    except:
        db.session.rollback()
        return ('Movie is already in the selected Watchlist.', 202)

    return ('Added to your Watchlist!', 200)

@bp_watchlists.route('/watchlists/<int:list_id>/remove_movie/<int:movie_id>', methods=['POST'])
def remove_movie_from_watchlist(list_id, movie_id):

    # restrict action to logged in user
    # authorize current user is owner of current watchlist
    curr_list = Watchlist.query.get(list_id)
    if curr_list.user_id != current_user.id or current_user.is_anonymous:
        return('',403)

    watchlist_entry = Watchlist_Movie.query.filter_by(watchlist_id=list_id, movie_id=movie_id).first()
    movie = SavedMovie.query.get(movie_id)
    title = movie.title
    db.session.delete(watchlist_entry)
    db.session.commit()
    flash(f'Removed "{title}" from list','warning')
    return redirect(f'/watchlists/{list_id}')

@bp_watchlists.route('/watchlists/<int:list_id>')
def show_watchlist_detail(list_id):
    # list editing options should be displayed for authorized users
    watchlist = Watchlist.query.get_or_404(list_id)
    if current_user.is_authenticated:
        is_owner = True if watchlist.user_id == current_user.id else False
    else:
        is_owner = False
    return render_template('watchlists/watchlist_detail.html', watchlist=watchlist, is_owner=is_owner)

@bp_watchlists.route('/watchlists/new', methods=['GET','POST'])
@login_required
def new_watchlist():
    form = NewWatchlistForm()
    if form.validate_on_submit():
        watchlist = Watchlist(
            title = form.title.data,
            description = form.description.data,
            is_shared = form.is_shared.data,
            user_id = current_user.id
        )
        db.session.add(watchlist)
        db.session.commit()
        flash(f'Watchlist "{watchlist.title}" successfully added','info')
        return redirect('/my_lists')
    else:
        return render_template('watchlists/watchlist_new.html', form=form)

@bp_watchlists.route('/watchlists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_watchlist(list_id):
    watchlist = Watchlist.query.get_or_404(list_id)
    title = watchlist.title
    db.session.delete(watchlist)
    db.session.commit()
    flash(f'Watchlist "{title}" deleted','warning')
    return redirect(f'/user/{current_user.id}/watchlists')

@bp_watchlists.route('/watchlists/<int:list_id>/edit', methods=['GET','POST'])
@login_required
def edit_watchlist(list_id):
    watchlist = Watchlist.query.get_or_404(list_id)
    if current_user.id == watchlist.user_id:
        form = EditWatchlistForm(obj=watchlist)
        if form.validate_on_submit():
            watchlist.title = form.title.data
            watchlist.description = form.description.data
            watchlist.is_shared = form.is_shared.data
            db.session.commit()
            flash('Changes successfully made to watchlist','info')
            return redirect(f'/user/{current_user.id}/watchlists')
        return render_template('watchlists/watchlist_edit.html', form=form)
    else:
        return('',403)

@bp_watchlists.route('/user/<int:user_id>/watchlists')
@login_required
def user_watchlists(user_id):
    if current_user.id == user_id:
        watchlists = Watchlist.query.filter_by(user_id=user_id).all()
        return render_template('user/my_watchlists.html', watchlists=watchlists)
    else:
        return('',403)

@bp_watchlists.route('/my_lists')
@login_required
def redirect_to_user_watchlists():
    return redirect(f'/user/{current_user.id}/watchlists')