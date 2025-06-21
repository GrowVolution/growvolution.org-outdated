from .rendering import render, render_404
from .logic.blog import (preview as blog_preview, create as blog_creator,
                         post as blog_post_handler, edit as blog_edit_handler)
from .logic.user import (profile as profile_handler, reflection as reflection_handler, journey as journey_handler,
                         week as week_handler)
from .logic import index as index_handler
from .routing import require_user, require_admin
from flask import Blueprint, redirect
from LIBRARY import ALL_METHODS, POST_METHOD

routes = Blueprint('routes', __name__)
blog_routes = Blueprint('blog_routes', __name__)
journey_routes = Blueprint('journey_routes', __name__)
week_routes = Blueprint('week_routes', __name__)


# Main Routes
@routes.route('/')
def index():
    return index_handler.handle_request()


@routes.route('/initiator')
def initiator():
    return render('site/initiator.html')


# Blog routes
@blog_routes.route('/')
def blog():
    return blog_preview.handle_request()


@blog_routes.route('/<blog_id>')
def blog_post(blog_id):
    return blog_post_handler.handle_request(blog_id)


@blog_routes.route('/<blog_id>/edit', methods=POST_METHOD)
@require_user(True)
def blog_edit(user, blog_id):
    return blog_edit_handler.handle_request(user, blog_id)


@blog_routes.route('/new', methods=ALL_METHODS)
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


@journey_routes.route('/')
@require_user(False)
def journey(user):
    return journey_handler.handle_request(user)


@journey_routes.route('/start', methods=POST_METHOD)
@require_user(True)
def journey_start(user):
    return journey_handler.start_journey(user)


@journey_routes.route('/daily_track', methods=POST_METHOD)
@require_user(True)
def daily_track(user):
    return journey_handler.daily_track(user)


@journey_routes.route('/text-correct')
@require_user(False)
def journey_text_correct(user):
    return journey_handler.text_correct(user)


@journey_routes.route('/update', methods=POST_METHOD)
@require_user(True)
def journey_update(user):
    return journey_handler.update_journey(user)


@week_routes.route('/')
@require_user(False)
def week(user):
    return week_handler.handle_request(user)


@week_routes.route('/setup', methods=POST_METHOD)
@require_user(True)
def setup_week(user):
    return week_handler.setup_week(user)


@week_routes.route('/edit')
@require_user(False)
def edit_week(user):
    return week_handler.edit_week(user)


@week_routes.route('/update', methods=POST_METHOD)
@require_user(True)
def update_week(user):
    return week_handler.update_week(user)


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


routes.register_blueprint(blog_routes, url_prefix='/blog')
routes.register_blueprint(journey_routes, url_prefix='/journey')
routes.register_blueprint(week_routes, url_prefix='/week')
