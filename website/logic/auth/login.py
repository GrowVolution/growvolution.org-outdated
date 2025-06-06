from website.rendering import render
from website.data import user as udb
from .verification import token_response
from flask import Response, request, flash
from markupsafe import Markup


def _render_self(**kwargs) -> str:
    return render('auth/login.html', **kwargs)


def handle_request() -> Response | str:
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = udb.User.query.filter_by(email=email).first()

        if not user:
            flash(Markup("Es existiert kein account mit dieser E-Mail Adresse. "
                         "Möchtest du dich <a href='/signup'>hier registrieren</a>?"), 'warning')
            return _render_self()

        api_flag = user.oauth_provider

        if api_flag:
            api = api_flag.capitalize()
            flash(Markup(f"Dieser Account ist mit {api} verknüpft. "
                         f"Bitte melde dich mit <a href='/oauth/{api_flag}/start'>{api}</a> an."), 'warning')
            return _render_self()

        if not user.check_password(password):
            flash("Das eingegebene Passwort war leider falsch!", 'danger')
            return _render_self(email=email)

        return token_response({
            "id": user.id
        }, 10)

    return _render_self()