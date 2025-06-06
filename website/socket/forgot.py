from website.data import user as udb
from mail_service import reset_mail
from website.cache import add_entry
from flask import render_template
from markupsafe import Markup


def handle_html_request():
    from . import emit_html
    emit_html(render_template('auth/forgot.html'))


def _check_user(user: udb.User) -> bool:
    from . import socket_flash
    if not user:
        socket_flash("Es existiert kein Account mit dieser E-Mail Adresse.", 'danger')
        return False

    api_flag = 'Google' if user.google_id else (
        'Apple' if user.apple_id else (
        'Microsoft' if user.microsoft_id else None)
    )
    if api_flag:
        socket_flash(f"Diese E-Mail Adresse ist mit einem {api_flag} Account verknüpft."
                     f" Du kannst dein Passwort nur über deinen Anbieter zurücksetzen.", 'warning')
        return False

    return True


def handle_reset_request(email: str):
    user = udb.User.query.filter_by(email=email).first()
    success = _check_user(user)
    if success:
        code = add_entry(user.id, 10)
        reset_mail(email, user.first_name, code)

        from . import emit, emit_html
        emit_html(Markup("<div class='text-center'><b class='text-success'>"
                         "Wir haben dir einen Link zum Zurücksetzen deines Passworts geschickt! "
                         "Dieser ist 10 Minuten gültig."
                         "</b></div>"))
        emit('success')
