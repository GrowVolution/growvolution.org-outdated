from website.utils.rendering import render
from website.data import journal as journal_db
from website.socket.messages import send_message
from shared.data import commit, add_model
from flask import request, redirect
from datetime import datetime, timedelta
import json


def _to_journal_history():
    return redirect('/journal/history')


def handle_request(user):
    last_entry = (
        journal_db.JournalData.query
        .filter_by(uid=user.id)
        .order_by(journal_db.JournalData.timestamp.desc())
        .first()
    )
    can_add_entry = (datetime.now() - last_entry.timestamp >= timedelta(days=1)) if last_entry else True
    if not can_add_entry:
        return _to_journal_history()

    return render('user/journal/journal.html')


def journal_history():
    return render('user/journal/history.html')


def set_journal(user):
    questions_str = request.get_json().get('questions', '')
    user.set_journal(questions_str)
    user.add_xp(0 if user.journal_created else 25)
    commit()

    send_message('score_update')
    return '', 200


def add_entry(user):
    raw_data = request.form
    setup = user.journal_setup_data or []
    entry_data = []

    for index, question in enumerate(setup):
        field_name = f"q_{index}"
        q_type = question.get("type")
        q_label = question.get("question", "").strip()

        if q_type == "checkbox":
            value = field_name in raw_data
        else:
            value = raw_data.get(field_name, "").strip()

        entry_data.append({
            "label": q_label,
            "value": value
        })

    json_string = json.dumps(entry_data, ensure_ascii=False)
    new_entry = journal_db.JournalData(user.id, json_string)
    user.add_xp(5)
    add_model(new_entry)

    return _to_journal_history()
