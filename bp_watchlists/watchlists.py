from flask import Blueprint, render_template

bp_watchlists = Blueprint('bp_watchlists', __name__,
    template_folder='templates',
    static_folder='static')