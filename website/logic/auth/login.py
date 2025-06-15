from website.rendering import render
from website.data import user as udb
from mail_service import login_notify
from .verification import token_response
from flask import Response, request, flash
from markupsafe import Markup


def _render_self(**kwargs) -> str:
    return render('auth/login.html', **kwargs)


def _render_2fa(email: str) -> str:
    return render('auth/2fa_confirm.html', email=email)


def _2fa_check(user: udb.User, otp: str) -> Response | str:
    if not user.check_2fa_token(otp):
        flash("Das Einmalpasswort ist ungültig oder abgelaufen.", "danger")
        return _render_2fa(user.email)

    if len(otp) == 8:
        flash("Du hast dich mit einem Wiederherstellungscode eingeloggt. Dieser ist nun nicht mehr verfügbar.", "info")

    notify(user)
    return _login_success(user.id)


def _login_success(user_id: int) -> Response:
    return token_response({
        "id": user_id
    }, 10)


def notify(user):
    if user.login_notify:
        login_notify(user.email, user.first_name)


def handle_request() -> Response | str:
    if request.method == "POST":
        email = request.form.get("email")

        user = udb.User.query.filter_by(email=email).first()
        if not user:
            flash(Markup("Es existiert kein account mit dieser E-Mail Adresse. "
                         "Möchtest du dich <a href='/signup'>hier registrieren</a>?"), 'warning')
            return _render_self()

        otp = request.form.get('otp')
        if otp:
            return _2fa_check(user, otp)

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

        elif user.twofa_enabled:
            return _render_2fa(email)

        notify(user)
        return _login_success(user.id)

    return _render_self()