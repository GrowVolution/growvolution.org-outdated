from . import token_response
from website import DEBUG
from website.utils.rendering import render
from website.utils.mail_service import login_notify
from website.data.user import User
from website.data.dev import DevToken
from flask import Response, request, flash, redirect, session
from markupsafe import Markup


def _render_self(**kwargs) -> str:
    return render('auth/login.html', **kwargs)


def _render_dev() -> str:
    return render('auth/dev_login.html')


def login_success(user_id: int, twofa_confirmed: bool = False) -> Response:
    return token_response({
        "id": user_id,
        "twofa_confirmed": 'true' if twofa_confirmed else 'false'
    }, 10)


def notify(user):
    if user.login_notify:
        login_notify(user.email, user.first_name)


def handle_dev_login() -> Response | str:
    if DEBUG:
        return redirect("https://growvolution.org/login/dev")

    if not session.get('dev_login_info'):
        session['dev_login_info'] = 'notified'
        flash("Dev-Cookies werden zur globalen Verifizierung über die Hauptseite geladen.", 'info')

    if request.method == "POST":
        token_name = request.form.get("name")
        token = DevToken.query.filter_by(name=token_name).first()
        if not token:
            flash("Es existiert kein Token mit dieser Bezeichnung", 'warning')
            return _render_dev()

        elif not token.valid:
            flash("Dieses Token ist abgelaufen!", 'danger')
            return _render_dev()

        elif token.token != request.form.get("token"):
            flash("Falsches Token!", 'danger')
            return _render_dev()

        return token_response({
            "id": token.id
        }, 5, 'dev_token', dev=True)

    return _render_dev()


def handle_request() -> Response | str:
    if request.method == "POST":
        email = request.form.get("email")

        user = User.query.filter_by(email=email).first()
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

        password = request.form.get("password")
        if not user.check_password(password):
            flash("Das eingegebene Passwort war leider falsch!", 'danger')
            return _render_self(email=email)

        notify(user)
        return login_success(user.id)

    return _render_self()