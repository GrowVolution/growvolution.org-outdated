from website.rendering import render
from website.data import commit, add_model, journey as journey_db
from website.socket.messages import send_message
from flask import request, redirect


def _back_to_journey():
    return redirect('/journey')


def handle_request(user):
    return render('user/journey.html', user=user)


def start_journey(user):
    data = request.form

    user.start_journey(
        vision=data.get("vision", ""),
        intention=data.get("intention", ""),
        discipline=int(data.get("discipline", 0)),
        energy=int(data.get("energy", 0)),
        focus=int(data.get("focus", 0)),
        goal_5y=data.get("goal_5y", ""),
        goal_1y=data.get("goal_1y", ""),
        goal_quarter=data.get("goal_quarter", ""),
        goal_month=data.get("goal_month", ""),
        goal_week=data.get("goal_week", "")
    )
    user.add_xp(100)
    commit()

    send_message('score_update')
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
