from flask import Flask, request, render_template, redirect, flash, session, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from models import db, User, Watchlist
from api.api_requests import get_data
from forms import MovieSearchForm
import json
from os import environ

bp_search = Blueprint('bp_search', __name__, template_folder='templates', static_folder='static')

@bp_search.route('/search', methods=['GET', 'POST'])
def show_search():
    form = MovieSearchForm()
    if form.validate_on_submit():
        # save form data to session, send to results page 1
        session['audio'] = form.audio.data
        session['subs'] = form.subs.data
        session['start_year'] = form.year_from.data
        session['end_year'] = form.year_to.data
        session['filter_movie'] = form.filter_movie.data
        session['filter_series'] = form.filter_series.data
        try:
            data = json.loads(response)
            movies = data['results']
            total = data['total']
        except:
            movies = None
        return redirect('/search/results/1')
    else:
        if 'total' in session:
            session.pop('total')
        return render_template('search/search_home.html', form=form)

@bp_search.route('/search/results/<int:page_num>')
def get_next_search_page(page_num):
    results_per_page = 12
    response = get_data(
            audio = session['audio'],
            subs = session['subs'],
            start_year = session['start_year'],
            end_year = session['end_year'],
            filter_movie = session['filter_movie'],
            filter_series = session['filter_series'],
            offset = ((page_num-1)*results_per_page),
            )
    movies = json.loads(response)
    # store total results found because it is only available on page 1 of request
    if page_num == 1:
        session['total'] = movies['total']
    
    if session['total'] == 0:
        return render_template('search/search_noresults.html')
    else:
        return render_template(
            'search/search_results.html',
            movies=movies['results'],
            total=session['total'],
            audio=session['audio'],
            subs=session['subs'],
            page=page_num,
            next_page=(page_num+1),
            result_start=(((page_num-1)*results_per_page)+1),
            result_end=(page_num*results_per_page),
            )
