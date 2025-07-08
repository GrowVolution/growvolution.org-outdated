from . import register_event, require_user
from .. import emit , socket_flash
from ..messages import send_message
from website.data import user as udb, commit
from website.utils import normalize_phone
from website.utils.cache import add_entry, request_entry_data, pop_entry
from website.utils.mail_service import email_change_mail
from datetime import datetime
import pyotp


@register_event('onboarding_done')
@require_user(False)
def finish_onboarding(user):
    user.onboarding_shown = True
    commit()


@register_event('check_username')
def check_username(data):
    value = (data.get('value') or '').strip()
    available = bool(value) and not udb.User.query.filter_by(username=value).first()
    emit('username_status', {'available': available})


@register_event('update_username')
@require_user(True)
def update_username(user, data):
    new_name = (data.get('username') or '').strip()
    if not user.can_change_username():
        socket_flash("Du kannst deinen Nutzernamen nur alle 30 Tage ändern.", "warning")
    elif not new_name or udb.User.query.filter_by(username=new_name).first():
        socket_flash("Dieser Benutzername ist bereits vergeben.", "danger")
    else:
        user.set_username(new_name)
        commit()
        emit('username_updated', {'success': True, 'username': user.username})


@register_event('change_password')
@require_user(True)
def change_password(user, data):
    current = data.get('current') or ''
    new = data.get('new') or ''
    if not user.check_password(current):
        socket_flash("Aktuelles Passwort ist falsch.", "danger")
    else:
        user.set_password(new)
        commit()
        emit('password_changed', {'success': True})


@register_event('confirm_2fa')
@require_user(True)
def confirm_2fa(user, data):
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
    commit()

    emit('2fa_confirmed', {'success': True, 'recovery_codes': recovery_codes})


@register_event('disable_2fa')
@require_user(True)
def disable_2fa(user):
    user.disable_2fa()
    commit()
    emit('2fa_disabled', {'success': True})


@register_event('toggle_login_notify')
@require_user(True)
def toggle_login_notify(user, data):
    enable = bool(data.get('enable'))
    user.login_notify = enable
    commit()
    emit('login_notify_updated', {'enabled': enable})


@register_event('request_email_change')
@require_user(True)
def request_email_change(user, data):
    new_email = (data.get('email') or '').strip()

    if not new_email:
        socket_flash("Dein Account muss mit einer E-Mail verknüpft sein.", 'warning')
        return

    if udb.User.query.filter_by(email=new_email).first():
        socket_flash("Diese E-Mail wird bereits verwendet.", "danger")
        return

    code = add_entry(new_email, 10)
    user.email_change_code = code
    commit()

    email_change_mail(new_email, user.first_name, code)
    emit('email_change_requested', {'success': True, 'email': new_email})



@register_event('update_phone')
@require_user(True)
def update_phone(user, data):
    phone = data.get('phone')
    if phone is None:
        user.phone = None
        user.remove_xp(30)
    else:
        prefix = phone.get('prefix', '')
        number = phone.get('number', '').lstrip('0')
        user.phone = normalize_phone(prefix + number)
        user.add_xp(30)

    commit()
    send_message('score_update')
    emit('phone_updated', {'success': True, 'phone': {'prefix': prefix, 'number': number} if phone else None})


@register_event('update_address')
@require_user(True)
def update_address(user, data):
    addr = data.get('address')
    if addr is None:
        user.address = None
    elif isinstance(addr, dict):
        street = addr.get('street')
        number = addr.get('number')
        postal = addr.get('postal')
        city = addr.get('city')
        user.set_address(street, number, postal, city)
    commit()
    emit('address_updated', {'success': True, 'address': user.address_str})


@register_event('update_birthday')
@require_user(True)
def update_birthday(user, data):
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
    emit('birthday_updated', {'success': True, 'birthday': user.birthdate.strftime('%d.%m.%Y')})


@register_event('update_gender')
@require_user(True)
def update_gender(user, data):
    gender = data.get('gender') or ''
    if gender not in ('m', 'w', 'd', ''):
        socket_flash("Ungültige Auswahl.", "danger")
        return
    user.gender = gender or None
    commit()
    emit('gender_updated', {'success': True, 'gender': user.gender})


@register_event('set_setting')
@require_user(True)
def set_setting(user, data):
    if not isinstance(data, dict) or len(data) != 1:
        emit('setting_updated', {'success': False})
        return

    key, value = next(iter(data.items()), (None, None))

    if not hasattr(user, key):
        emit('setting_updated', {'success': False})
        return

    setattr(user, key, value)
    commit()
    emit('setting_updated', {'success': True})
