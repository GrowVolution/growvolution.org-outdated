from .. import require_user, METHODS
from website.logic.user import journey as journey_handler
from flask import Blueprint

journey = Blueprint('journey', __name__)


@journey.route('/')
@require_user(False)
def main(user):
    return journey_handler.handle_request()


@journey.route('/history')
@require_user(False)
def journey_history(user):
    return journey_handler.journey_history(user)


@journey.route('/start', methods=METHODS.POST)
@require_user(True)
def journey_start(user):
    return journey_handler.start_journey(user)


@journey.route('/daily_track', methods=METHODS.POST)
@require_user(True)
def daily_track(user):
    return journey_handler.daily_track(user)


@journey.route('/weekly_track', methods=METHODS.POST)
@require_user(True)
def weekly_track(user):
    return journey_handler.weekly_track(user)


@journey.route('/text-correct')
@require_user(False)
def journey_text_correct(user):
    return journey_handler.text_correct(user)


@journey.route('/update', methods=METHODS.POST)
@require_user(True)
def journey_update(user):
    return journey_handler.update_journey(user)
