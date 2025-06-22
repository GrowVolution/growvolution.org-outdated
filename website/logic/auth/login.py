from . import token_response
from website.utils.rendering import render
from website.utils.mail_service import login_notify
from website.data.user import User
from flask import Response, request, flash
from markupsafe import Markup


def _render_self(**kwargs) -> str:
    return render('auth/login.html', **kwargs)


def login_success(user_id: int, twofa_confirmed: bool = False) -> Response:
    return token_response({
        "id": user_id,
        "twofa_confirmed": 'true' if twofa_confirmed else 'false'
    }, 10)


def notify(user):
    if user.login_notify:
        login_notify(user.email, user.first_name)


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