from website.data import commit
from website.socket.messages import send_message
from website.utils.rendering import render
from flask import request, flash, redirect
import json


def handle_initial_reflection(user):
    state = request.form.get("current", "").strip()
    goal = request.form.get("goal", "").strip()
    focus_raw = request.form.get("focus", "[]")
    steps_raw = request.form.get("steps", "[]")
    step_thoughts = request.form.get("stepThoughts", "").strip()
    phone = request.form.get("phone", "").strip()
    consent = request.form.get("consent", "0") == "1"

    focus = json.loads(focus_raw)
    steps = json.loads(steps_raw)

    user.initial_reflection(
        state=state,
        goal=goal,
        focus=focus,
        steps=steps,
        step_thoughts=step_thoughts
    )

    if phone:
        user.set_phone(phone)
        user.contact_consent = consent

    user.add_xp(130 if phone and consent else 100)
    commit()

    send_message('score_update')
    return '', 200


def foundation(user):
    return render('user/foundation.html', user)


def update_foundation(user):
    current = (request.form.get("current") or "").strip()
    goal = (request.form.get("goal") or "").strip()
    step_thoughts = (request.form.get("step_thoughts") or "").strip()
    focus = request.form.getlist("focus")
    steps = request.form.getlist("steps")

    user.initial_reflection(current, goal, focus, steps, step_thoughts)
    commit()

    flash("Dein Fundament wurde aktualisiert!", "success")
    return redirect('/foundation')
