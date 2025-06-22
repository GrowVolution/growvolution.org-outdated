from . import require_user
from website.logic.user.profile import twofa_setup as handle_2fa_setup
from flask import Blueprint

api = Blueprint('api', __name__)


@api.route('/2fa-setup')
@require_user(True)
def twofa_setup(user):
    return handle_2fa_setup(user)
