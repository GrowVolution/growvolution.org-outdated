from website.data import user as udb, commit
from website.logic.auth.verification import get_user
from website.cache import add_entry, request_entry_data, pop_entry
from mail_service import email_change_mail
from datetime import datetime
import pyotp


def emit(event, data, **kwargs):
    from . import emit as socket_emit
    socket_emit(event, data, **kwargs)


def socket_flash(msg, cat):
    from . import socket_flash as flash
    flash(msg, cat)


def require_user(fn):
    def wrapper(data):
        user = get_user()
        if not user:
            socket_flash("Nicht authentifiziert!", "danger")
            return
        fn(data, user)
    return wrapper


def check_username(data):
    value = (data.get('value') or '').strip()
    available = bool(value) and not udb.User.query.filter_by(username=value).first()
    emit('username_status', {'available': available})


@require_user
def update_username(data, user):
    new_name = (data.get('username') or '').strip()
    if not user.can_change_username():
        socket_flash("Du kannst deinen Nutzernamen nur alle 30 Tage ändern.", "warning")
    elif not new_name or udb.User.query.filter_by(username=new_name).first():
        socket_flash("Dieser Benutzername ist bereits vergeben.", "danger")
    else:
        user.username = new_name
        user.username_changed_at = datetime.utcnow()
        commit()
        emit('username_updated', {'success': True})


@require_user
def change_password(data, user):
    current = data.get('current') or ''
    new = data.get('new') or ''
    if not user.check_password(current):
        socket_flash("Aktuelles Passwort ist falsch.", "danger")
    else:
        user.set_password(new)
        emit('password_changed', {'success': True})


@require_user
def confirm_2fa(data, user):
    from . import emit, socket_flash

    token = (data.get("token") or "").strip()
    cache_code = data.get('secret_entry') or ''
    secret = request_entry_data(cache_code)
    if not token or not secret:
        socket_flash("Fehlende oder ungültige Eingabe.", "danger")
        return

    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        socket_flash("Der Code ist ungültig oder abgelaufen.", "danger")
        return

    pop_entry(cache_code)
    recovery_codes = user.enable_2fa(secret)

    emit('2fa_confirmed', {'success': True, 'recovery_codes': recovery_codes})


@require_user
def disable_2fa(data, user):
    user.disable_2fa()
    emit('2fa_disabled', {'success': True})


@require_user
def toggle_login_notify(data, user):
    enable = bool(data.get('enable'))
    user.login_notify = enable
    commit()
    emit('login_notify_updated', {'enabled': enable})


@require_user
def request_email_change(data, user):
    email = (data.get('email') or '').strip()
    if not email or udb.User.query.filter_by(email=email).first():
        socket_flash("Diese E-Mail-Adresse ist ungültig oder bereits vergeben.", "danger")
    else:
        entry_data = {
            'user': user,
            'email': email
        }
        code = add_entry(entry_data, 10)
        email_change_mail(email, user.first_name, code)
        emit('email_change_requested', {'success': True})


@require_user
def update_phone(data, user):
    phone = data.get('phone')
    if phone is None:
        user.phone = None
    elif isinstance(phone, dict):
        prefix = phone.get('prefix')
        number = phone.get('number')
        user.phone = f"{prefix} {number}".strip() if prefix and number else None
    commit()
    emit('phone_updated', {'success': True})


@require_user
def update_address(data, user):
    addr = data.get('address')
    if addr is None:
        user.address = None
    elif isinstance(addr, dict):
        street = addr.get('street')
        number = addr.get('number')
        postal = addr.get('postal')
        city = addr.get('city')
        user.set_address(street, number, postal, city)
    emit('address_updated', {'success': True})


@require_user
def update_birthday(data, user):
    birthday = data.get('birthday')
    if birthday is None:
        user.birthdate = None
    else:
        try:
            user.birthdate = datetime.strptime(birthday, "%Y-%m-%d").date()
        except ValueError:
            socket_flash("Ungültiges Datumsformat.", "danger")
            return
    commit()
    emit('birthday_updated', {'success': True})


@require_user
def update_gender(data, user):
    gender = data.get('gender') or ''
    if gender not in ('m', 'w', 'd', ''):
        socket_flash("Ungültige Auswahl.", "danger")
        return
    user.gender = gender or None
    commit()
    emit('gender_updated', {'success': True})
