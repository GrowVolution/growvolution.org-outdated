from .logic.user.profile import twofa_setup as handle_2fa_setup
from .routing import require_user
from flask import Blueprint

api_routes = Blueprint('api_routes', __name__)


@api_routes.route('/2fa-setup')
@require_user(True)
def twofa_setup(user):
    return handle_2fa_setup(user)
