from ..utils.rendering import render, render_404
from flask import Blueprint

site = Blueprint('people_site', __name__)


@site.route('/')
def index():
    return render('site/index.html')


# Statutes
@site.route('/statutes/<struct>')
def statutes(struct):
    match struct:
        case 'association':
            return render('site/association_statute.html')
        case _:
            return render_404()


@site.route('/<path:path>')
def not_found(path):
    return render_404()
