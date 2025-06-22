from .. import require_user, METHODS
from website.logic.user import profile as profile_handler, reflection as reflection_handler
from flask import Blueprint

user = Blueprint('user', __name__)


def init_routes():
    from .journey import journey
    from .journal import journal
    from .week import week

    user.register_blueprint(journey, url_prefix='/journey')
    user.register_blueprint(journal, url_prefix='/journal')
    user.register_blueprint(week, url_prefix='/week')


@user.route('/profile')
@require_user(False)
def profile(usr):
    return profile_handler.handle_request(usr)


@user.route('/confirm-mail-change/<code>')
def confirm_mail_change(code):
    return profile_handler.handle_mail_change(code)


@user.route('/initial-reflection', methods=METHODS.POST)
@require_user(True)
def initial_reflection(usr):
    return reflection_handler.handle_initial_reflection(usr)


@user.route('/foundation')
@require_user(False)
def foundation(usr):
    return reflection_handler.foundation(usr)


@user.route('/foundation/update', methods=METHODS.POST)
@require_user(True)
def foundation_update(usr):
    return reflection_handler.update_foundation(usr)
