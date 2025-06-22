from .. import require_user, METHODS
from website.logic.user import week as week_handler
from flask import Blueprint

week = Blueprint('week', __name__)


@week.route('/')
@require_user(False)
def main(user):
    return week_handler.handle_request(user)


@week.route('/setup', methods=METHODS.POST)
@require_user(True)
def setup_week(user):
    return week_handler.setup_week(user)


@week.route('/edit')
@require_user(False)
def edit_week(user):
    return week_handler.edit_week(user)


@week.route('/update', methods=METHODS.POST)
@require_user(True)
def update_week(user):
    return week_handler.update_week(user)
