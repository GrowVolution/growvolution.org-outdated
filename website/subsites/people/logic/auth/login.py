from ...utils.rendering import render
from ...data.user import PeopleUser
from website.logic.auth import token_response
from flask import request, flash


def _render_self(**kwargs):
    return render('auth/login.html', **kwargs)


def handle_request():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = PeopleUser.query.filter_by(email=email).first()
        if not user:
            flash("Es existiert kein Account mit dieser Email-Adresse.", 'warning')
            return _render_self()

        if user.temporary:
            flash("Dieser Account ist noch nicht freigeschaltet!", 'warning')
            return _render_self()

        if not user.check_password(password):
            flash("Das eingegebene Passwort war leider falsch!", 'danger')
            return _render_self(email=email)

        return token_response({
            "id": user.id
        }, 10)

    return _render_self()
