from .rendering import render, render_404
from .logic.auth.verification import is_admin
from .logic.blog import (preview as blog_preview, create as blog_creator,
                         post as blog_post_handler, edit as blog_edit_handler)
from .logic.user import profile as profile_handler, reflection as reflection_handler
from .logic import index as index_handler
from .routing import require_user, require_admin
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
@require_user(True)
def blog_edit(user, blog_id):
    return blog_edit_handler.handle_request(user, blog_id)


@routes.route('/blog/new', methods=ALL_METHODS)
@require_admin(False)
def new_blog_post():
    return blog_creator.handle_request()


# User routes
@routes.route('/profile')
@require_user(False)
def profile(user):
    return profile_handler.handle_request(user)


@routes.route('/confirm-mail-change/<code>')
def confirm_mail_change(code):
    return profile_handler.handle_mail_change(code)


@routes.route('/initial-reflection', methods=POST_METHOD)
@require_user(True)
def initial_reflection(user):
    return reflection_handler.handle_initial_reflection(user)


@routes.route('/foundation')
@require_user(False)
def foundation(user):
    return reflection_handler.foundation(user)


@routes.route('/foundation/update', methods=POST_METHOD)
@require_user(True)
def foundation_update(user):
    return reflection_handler.update_foundation(user)


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