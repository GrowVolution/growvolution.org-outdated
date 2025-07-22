from website import APP
from website.data.user import User
from website.data.dev import DevToken
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
                   response: Response | str | None = None, status=302, dev=False) -> Response:
    expiration = timedelta(days=expiration_days)
    max_age = expiration_days * 24 * 60 * 60
    data['exp'] = datetime.now() + expiration

    if name != 'captcha_token':
        data['fingerprint'] = token_owner_hash('captcha_token')

    token = jwt.encode(data, APP.config['SECRET_KEY'], algorithm='HS256')

    res = make_response(response if response else back_home(), status)
    if dev:
        res.set_cookie(name, token, httponly=True, secure=True, max_age=max_age,
                       samesite=None, domain=".growvolution.org")
    else:
        res.set_cookie(name, token, httponly=True, secure=True, max_age=max_age)

    return res


def verify_token_ownership(name: str = 'token') -> Response | None:
    if request.is_json and request.get_json().get(f'verify_{name}'):
        fingerprint = request.headers.get('X-Client-Fingerprint')
        owner = token_owner_hash(name) == fingerprint
        if not owner:
            return empty_token(name)

        origin = request.cookies.get('origin')
        if origin:
            response = make_response(redirect(origin))
            response.set_cookie('origin', '', expires=0)
        else:
            response = make_response('', 204)

        if name == 'dev_token':
            response.set_cookie('dev_token_owner', 'true', httponly=True, secure=True,
                                samesite=None, domain=".growvolution.org")
        else:
            session[f'{name}_owner'] = True

        return response

    return None


def decoded_token(token) -> Any | None:
    try:
        return jwt.decode(token, key=APP.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except jwt.InvalidSignatureError:
        return None


def captcha_status() -> str:
    decoded = decoded_token(request.cookies.get('captcha_token'))
    return decoded.get('status') if decoded else 'unverified'


def twofa_status() -> bool:
    decoded = decoded_token(request.cookies.get('token'))
    return decoded.get('twofa_confirmed') if decoded else None


def token_owner_hash(name: str = 'token') -> str | None:
    decoded = decoded_token(request.cookies.get(name))
    return decoded.get('fingerprint') if decoded else None


def get_user() -> User | None:
    decoded = decoded_token(request.cookies.get('token'))
    return User.query.get(decoded['id']) if decoded else None


def is_dev() -> bool:
    decoded = decoded_token(request.cookies.get('dev_token'))
    token = DevToken.query.get(decoded.get('id')) if decoded else None
    return token and token.valid


def authenticated_user_request() -> bool:
    decoded = decoded_token(request.cookies.get('token'))
    return decoded is not None
