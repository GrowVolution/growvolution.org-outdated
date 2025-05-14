from website import APP
from website.data import user as udb
from flask import request, session, flash, Response, make_response, redirect
from datetime import datetime, timedelta
from typing import Any
from LIBRARY import back_home
import jwt


def start_callback() -> tuple[str | None, str | None]:
    if request.method == "POST":
        code = request.form.get("code")
        state = request.form.get("state")
    else:
        code = request.args.get("code")
        state = request.args.get("state")

    if state != session.get('state'):
        flash("OAuth Status ungültig!", 'danger')
        return None, None

    if not code:
        flash("OAuth Code fehlt!", 'danger')
        return None, None

    return code, state


def empty_token(name: str = 'token', path: str = '/') -> Response:
    response = make_response(redirect(path))
    response.set_cookie(name, '', expires=0)
    return response


def token_response(data: dict, expiration_days: int, name='token',
                   response: Response | str | None = None, status=302) -> Response:
    expiration = timedelta(days=expiration_days)
    max_age = expiration_days * 24 * 60 * 60
    data['exp'] = datetime.now() + expiration

    if name != 'captcha_token':
        data['fingerprint'] = token_owner_hash('captcha_token')

    token = jwt.encode(data, APP.config['SECRET_KEY'], algorithm='HS256')

    res = make_response(response if response else back_home(), status)
    res.set_cookie(name, token, httponly=True, secure=True, max_age=max_age)

    return res


def _decoded_token(token) -> Any | None:
    try:
        return jwt.decode(token, key=APP.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except jwt.InvalidSignatureError:
        return None


def captcha_status() -> str:
    decoded_token = _decoded_token(request.cookies.get('captcha_token'))
    return decoded_token.get('status') if decoded_token else 'unverified'


def token_owner_hash(name: str = 'token') -> str | None:
    decoded_token = _decoded_token(request.cookies.get(name))
    return decoded_token.get('fingerprint') if decoded_token else None


def get_user() -> udb.User | None:
    decoded_token = _decoded_token(request.cookies.get('token'))
    return udb.User.query.get(decoded_token['id']) if decoded_token else None


def user_role() -> str | None:
    user = get_user()
    return user.role if user else None


def authenticated_user_request() -> bool:
    decoded_token = _decoded_token(request.cookies.get('token'))
    return decoded_token is not None
