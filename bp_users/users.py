from flask import Blueprint

from flask import Flask, request, render_template, redirect, flash, session, url_for, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from api_requests import get_data, get_movie_detail
from forms import MovieSearchForm, LoginForm, RegisterForm, NewWatchlistForm, EditWatchlistForm, EditUserForm, PickWatchlistForMovieForm
from sqlalchemy.exc import IntegrityError
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from os import environ

bp_users= Blueprint('bp_users', __name__,
    template_folder='templates',
    static_folder='static')

@bp_users.route('/logout')
def logout():
    logout_user()
    flash('Logged out.','info')
    return redirect('/')

@bp_users.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data,
            password = form.password.data,
        )
        if user is False:
            flash('Invalid login details. Try Again.','danger')
            return redirect('/login')
        else:
            login_user(user, remember=form.remember.data)
            flash('Successfully logged in. Welcome back!','success')
            return redirect('/profile')
    return render_template('user/login.html', form=form)

@bp_users.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data,
            )
            db.session.commit()
        except IntegrityError:
            flash('Username taken.','warning')
            return render_template('user/register.html', form=form)
        login_user(user)
        create_list_for_new_user(user)
        return redirect('/')
    return render_template('user/register.html', form=form)

@login_required
def create_list_for_new_user(user):
    # create a private list for newly registered user
    title = f"{user.username}'s Watchlist"
    new_list = Watchlist(title=title, is_shared=False, user_id=user.id)
    db.session.add(new_list)
    db.session.commit()

@bp_users.route('/profile', methods=['GET'])
@login_required
def user_profile():
    return render_template('user/profile.html')

@bp_users.route('/user/<int:user_id>/edit', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    if current_user.id == user_id:
        form = EditUserForm(obj=current_user)
        if form.validate_on_submit():
            user = User.query.get(user_id)
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash('Changes successfully made to account','info')
            return redirect('/profile')

        return render_template('user/edit.html', user=current_user, form=form)
    else:
        return('unauthorized')

@bp_users.route('/user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    if current_user.id == user_id:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User account deleted.','warning')
        return redirect('/logout')
    else:
        return('',403)