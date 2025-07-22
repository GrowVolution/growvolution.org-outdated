from ..logic.auth import login as login_handler
from website.utils.processing import protect_route
from website.logic.auth import empty_token
from website.routing import METHODS
from flask import Blueprint

auth = Blueprint('auth', __name__)
protected = Blueprint('protected', __name__)


@protected.before_request
def protect_request():
    return protect_route()


@protected.route('/login', methods=METHODS.ALL)
def login():
    return login_handler.handle_request()


@protected.route('/account-request', methods=METHODS.ALL)
def account_request():
    pass


@protected.route('/logout')
def logout():
    return empty_token()


auth.register_blueprint(protected)
