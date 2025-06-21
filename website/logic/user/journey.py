from website.rendering import render
from website.data import commit, add_model, journey as journey_db, user as udb
from website.data.helpers import normalize_timestamp
from website.socket.messages import send_message
from website.jobs import register_job, queue_job
from datetime import datetime
from flask import request, redirect


def _back_to_journey():
    return redirect('/journey')


def handle_request(user):
    return render('user/journey.html', user)


@register_job('journey_start')
def process_journey_start(app, data, user_id):
    with app.app_context():
        user = udb.User.query.get(user_id)
        user.start_journey(
            vision=data.get("vision", ""),
            intention=data.get("intention", ""),
            discipline=int(data.get("discipline", 0)),
            energy=int(data.get("energy", 0)),
            focus=int(data.get("focus", 0)),
            goal_5y=data.get("goal_5y", ""),
            goal_1y=data.get("goal_quarter", ""),
            goal_quarter=data.get("goal_1y", ""),
            goal_month=data.get("goal_month", ""),
            goal_week=data.get("goal_week", ""),
            text_correct=data.get("auto_correct", False) == '1'
        )
        user.add_xp(100)
        commit()

        send_message('score_update')


def start_journey(user):
    queue_job('journey_start', request.form, user.id)
    return '', 200


def daily_track(user):
    data = request.form

    journey_step = journey_db.Journey(user.id)
    journey_step.daily_track(
        mood_level=data.get("mood", 0),
        worked_on_goal=data.get("worked") == 'on',
        short_note=data.get("note", None),
        quick_motivation=data.get("motivation_text", None),
        motivation_type=data.get("motivation", None)
    )

    user.add_xp(10)
    user.new_day_tracked()
    add_model(journey_step)

    return _back_to_journey()


def update_journey(user):
    data = request.form
    allowed_fields = user.interval_border_data or []

    for field in allowed_fields:
        if field in data:
            value = data.get(field)
            if field.endswith('_rating'):
                setattr(user, field, int(value))
            else:
                setattr(user, field, value.strip())

    correct = 'correct' in data
    user.text_correct = correct

    if correct:
        user.journey_text_correct()

    user.last_updated = normalize_timestamp(datetime.now())
    commit()


def text_correct(user):
    user.journey_text_correct()
    user.text_correct = True
    commit()
    return _back_to_journey()
