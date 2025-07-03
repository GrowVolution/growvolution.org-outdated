from ..utils.rendering import render, render_404
from flask import Blueprint

site = Blueprint('banking_site', __name__)


@site.route('/')
def index():
    return render('site/index.html')


@site.route('/<path:path>')
def not_found(path):
    return render_404()
