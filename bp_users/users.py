from flask import Blueprint, render_template

bp_users= Blueprint('bp_users', __name__,
    template_folder='templates',
    static_folder='static')