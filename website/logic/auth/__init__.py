from website import APP
from website.data.user import User
from website.routing import back_home
from flask import request, Response, make_response, redirect, session
from datetime import datetime, timedelta
from typing import Any
import jwt


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


def verify_token_ownership(name: str = 'token') -> Response | None:
    if request.is_json and request.get_json().get(f'verify_{name}'):
        fingerprint = request.headers.get('X-Client-Fingerprint')
        owner = token_owner_hash(name) == fingerprint
        if not owner:
            return empty_token(name)

        session[f'{name}_owner'] = True
        return make_response('', 204)

    return None


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


def twofa_status() -> bool:
    decoded_token = _decoded_token(request.cookies.get('token'))
    return decoded_token.get('twofa_confirmed') if decoded_token else None


def token_owner_hash(name: str = 'token') -> str | None:
    decoded_token = _decoded_token(request.cookies.get(name))
    return decoded_token.get('fingerprint') if decoded_token else None


def get_user() -> User | None:
    decoded_token = _decoded_token(request.cookies.get('token'))
    return User.query.get(decoded_token['id']) if decoded_token else None


def user_role() -> str | None:
    user = get_user()
    return user.role if user else None


def is_admin() -> bool:
    role = user_role()
    return role == 'admin' or role == 'dev'


def authenticated_user_request() -> bool:
    decoded_token = _decoded_token(request.cookies.get('token'))
    return decoded_token is not None
