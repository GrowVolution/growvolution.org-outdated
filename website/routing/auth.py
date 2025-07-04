from . import METHODS
from website.logic.auth import (login as login_handler, signup as signup_handler, twofa,
                                confirm as confirm_handler, reset as reset_handler)
from website.logic.auth.oauth_flows import google, apple, microsoft
from website.logic.auth import empty_token
from website.utils.rendering import render_404
from website.utils.processing import protect_route
from flask import Blueprint

auth = Blueprint('auth', __name__)
protected = Blueprint('protected', __name__)


@protected.before_request
def protect_request():
    return protect_route()


@protected.route('/login', methods=METHODS.ALL)
def login():
    return login_handler.handle_request()


@protected.route('/login/dev', methods=METHODS.ALL)
def login_dev():
    return login_handler.handle_dev_login()


@protected.route('/signup', methods=METHODS.ALL)
def signup():
    return signup_handler.handle_request()


@auth.route('/notice/confirm/<code>')
def confirm_notice(code):
    return confirm_handler.confirm_notice(code)


@auth.route('/confirm/<code>')
def confirm(code):
    return confirm_handler.handle_confirm(code)


@auth.route('/reset/<code>', methods=METHODS.ALL)
def reset(code):
    return reset_handler.handle_request(code)


@auth.route('/oauth/<api>/start')
def start_oauth(api):
    return google.start_oauth() if api == 'google' else (
        apple.start_oauth() if api == 'apple' else (
            microsoft.start_oauth() if api == 'microsoft' else render_404()
        )
    )


@auth.route('/oauth/<api>/callback', methods=METHODS.ALL)
def oauth_callback(api):
    return google.oauth_callback() if api == 'google' else (
        apple.oauth_callback() if api == 'apple' else (
            microsoft.oauth_callback() if api == 'microsoft' else render_404()
        )
    )


@auth.route('/logout')
def logout():
    return empty_token()


auth.register_blueprint(protected)
