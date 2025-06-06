from .logic.user.profile import twofa_setup as handle_2fa_setup
from flask import Blueprint
from LIBRARY import POST_METHOD

api_routes = Blueprint('api_routes', __name__)


@api_routes.route('/2fa-setup')
def twofa_setup():
    return handle_2fa_setup()
