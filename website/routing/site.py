from . import back_home
from website.utils.rendering import render, render_404
from website.logic import index as index_handler
from flask import Blueprint

site = Blueprint('site', __name__)


# Main Routes
@site.route('/')
def index():
    return index_handler.handle_request()


@site.route('/initiator')
def initiator():
    return render('site/initiator.html')


# Legal Routes
@site.route('/about')
def about():
    return render("site/about.html")


@site.route('/privacy')
def privacy():
    return render("site/privacy.html")


@site.route('/guidelines')
def guidelines():
    return render("site/guidelines.html")


@site.route('/impressum')
def impressum():
    return render("site/impressum.html")


# Not Found
@site.route('/<path:path>')
def not_found(path):
    return render_404()


# Processing debug requests for testing
@site.route('/debug')
def debug():
    """

        TODO: Debug Stuff

    """
    raise Exception('Bewusst ausgelöster Fehler! - Debug Token Test.')
    return back_home()
