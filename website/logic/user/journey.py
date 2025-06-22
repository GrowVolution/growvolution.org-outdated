from website.utils.rendering import render, render_404
from website.utils.llm_api import correct_text
from website.data import commit, add_model, journey as journey_db, user as udb
from website.data.helpers import normalize_timestamp
from website.socket.messages import send_message
from website.jobs import register_job, queue_job
from datetime import datetime
from flask import request, redirect
from typing import Tuple


def _back_to_journey():
    return redirect('/journey')


def _tupled_value(value: str) -> Tuple[str, None]:
    return value, None


def handle_request(user):
    return render('user/journey/journey.html', user)


def journey_history(user):
    if not user.journey_started:
        return render_404()

    return render('user/journey/history.html', user)


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


def weekly_track(user):
    data = request.form
    correct = 'correct' in data
    user.text_correct = correct
    
    new_goal = data.get('goal_next_week', '')
    new_goal, rid = correct_text(new_goal) if correct else _tupled_value(new_goal)
    
    good = data.get('week_good', '')
    bad = data.get('week_bad', '')

    journey_step = journey_db.Journey(user.id)
    journey_step.weekly_track(user.goal_week, good, bad)
    user.goal_week = new_goal

    user.add_xp(10)
    user.new_day_tracked()
    add_model(journey_step)

    return _back_to_journey()


def update_journey(user):
    data = request.form
    allowed_fields = user.interval_border_data or []

    correct = 'correct' in data
    user.text_correct = correct
    
    rid = None
    for field in allowed_fields:
        if field in data:
            value = data.get(field)
            if field.endswith('_rating'):
                setattr(user, field, int(value))
            else:
                value = value.strip()
                value, rid = correct_text(value, rid) if correct else _tupled_value(value)
                setattr(user, field, value)
    
    user.last_updated = normalize_timestamp(datetime.now())
    commit()


def text_correct(user):
    user.journey_text_correct()
    user.text_correct = True
    commit()
    return _back_to_journey()
