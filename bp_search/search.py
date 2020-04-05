from flask import Blueprint, render_template

bp_search = Blueprint('bp_search', __name__,
    template_folder='templates',
    static_folder='static')