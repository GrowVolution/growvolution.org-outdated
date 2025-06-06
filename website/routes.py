from .rendering import render, render_404
from .logic.auth.verification import is_admin
from .logic.blog import (preview as blog_preview, create as blog_creator,
                         post as blog_post_handler, edit as blog_edit_handler)
from .logic.user import profile as profile_handler
from .logic import index as index_handler
from flask import Blueprint, redirect, flash
from LIBRARY import ALL_METHODS, POST_METHOD

routes = Blueprint('routes', __name__)


# Main Routes
@routes.route('/')
def index():
    return index_handler.handle_request()


# Blog routes
@routes.route('/blog')
def blog():
    return blog_preview.handle_request()


@routes.route('/blog/<blog_id>')
def blog_post(blog_id):
    return blog_post_handler.handle_request(blog_id)


@routes.route('/blog/<blog_id>/edit', methods=POST_METHOD)
def blog_edit(blog_id):
    return blog_edit_handler.handle_request(blog_id)


@routes.route('/blog/new', methods=ALL_METHODS)
def new_blog_post():
    if not is_admin():
        flash("Du bist leider nicht für das Erstellen von Blogeinträgen berechtigt.", 'danger')
        return redirect('/blog')

    return blog_creator.handle_request()


# User routes
@routes.route('/profile')
def profile():
    return profile_handler.handle_request()


# Legal Routes
@routes.route('/about')
def about():
    return render("site/about.html")


@routes.route('/privacy')
def privacy():
    return render("site/privacy.html")


@routes.route('/guidelines')
def guidelines():
    return render("site/guidelines.html")


@routes.route('/impressum')
def impressum():
    return render("site/impressum.html")


# Not Found
@routes.route('/<path:path>')
def not_found(path):
    return render_404()


# Processing debug requests for testing
@routes.route('/debug')
def debug():
    """

        TODO: Debug Stuff

    """
    return redirect('/')