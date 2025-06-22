from . import twofa_status, get_user
from .login import notify, login_success
from website.utils.rendering import render
from website.data.user import User
from flask import Response, flash, request


def render_2fa() -> str:
    return render('auth/2fa_confirm.html')


def twofa_check(user: User, otp: str) -> Response | str:
    if not user.check_2fa_token(otp):
        flash("Das Einmalpasswort ist ungültig oder abgelaufen.", "danger")
        return render_2fa()

    if len(otp) == 8:
        flash("Du hast dich mit einem Wiederherstellungscode eingeloggt. Dieser ist nun nicht mehr verfügbar.", "info")

    notify(user)
    return login_success(user.id, True)


def handle_2fa():
    user = get_user()
    if not user:
        return None

    elif not user.twofa_enabled:
        return None

    status = twofa_status()
    if status == 'true':
        return None

    otp = request.form.get('otp')
    if otp:
        return twofa_check(user, otp)

    return render_2fa()
