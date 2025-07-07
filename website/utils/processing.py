from . import random_code
from .. import APP, DEBUG
from ..socket import SOCKET
from ..socket.events import no_handler
from .rendering import render_error, render
from ..logic.auth import (captcha_status, verify_token_ownership, is_dev,
                          authenticated_user_request, get_user)
from ..logic.auth.captcha import handle_request as captcha
from ..logic.auth.twofa import handle_2fa
from ..data import commit
from ..routing import back_home, routes
from flask import request, abort, render_template, session, send_from_directory, redirect, make_response
from debugger import log
import sys, traceback, os


def _get_subsite():
    host = request.host
    subsite = host.split('.', 1)[0]
    return subsite if subsite not in {'growvolution', 'www'} else ''


@APP.context_processor
def context_processor():
    subsite = _get_subsite()
    subdomain = f"{subsite}." if subsite else ''
    return dict(
        subdomain=subdomain
    )


@routes.context_processor
def routes_context_processor():
    return dict(
        user=get_user()
    )


@APP.before_request
def before_request():
    method = request.method.upper()
    path = request.path
    ip = request.remote_addr
    agent = request.headers.get('User-Agent')
    agent = agent if agent else 'no-agent'

    log('request', f"{method} '{path:48}' from {ip:15} via ({agent}).")

    if path.startswith('/static'):
        filename = path.removeprefix('/static/')
        parts = filename.split('/', 1)

        root = APP.root_path
        static_folder_map = {
            'people': f'{root}/subsites/people/static',
            'learning': f'{root}/subsites/learning/static',
            'banking': f'{root}/subsites/banking/static',
        }

        subsite, file = parts if parts[0] in static_folder_map else ('', filename)

        static_folder = static_folder_map.get(subsite, APP.static_folder)
        return send_from_directory(static_folder, file)

    response = verify_token_ownership()
    if response:
        return response

    response = verify_token_ownership('dev_token')
    if response:
        return response

    safe_path = path.startswith('/socket.io')
    response = handle_2fa() if not safe_path else None
    if response:
        return response

    if authenticated_user_request() and not session.get("token_owner"):
        return render_template('auth/verify_token_ownership.html',
                               flag='verify_token')

    if is_dev() and not request.cookies.get('dev_token_owner'):
        host = request.host
        origin = f"https://{host}{path}" if not host.startswith('growvolution') else ''
        if origin:
            response = make_response(redirect("https://growvolution.org/verify"))
            response.set_cookie('origin', origin, httponly=True, secure=True,
                                samesite=None, domain=".growvolution.org")
            return response

        return render_template('auth/verify_token_ownership.html',
                               flag='verify_dev_token')

    def process_debug():
        subsite = os.getenv('DEBUG_SUBROUTING')

        match subsite:
            case 'people':
                from ..subsites.people.utils.processing import process_debug_request
            case 'learning':
                from ..subsites.learning.utils.processing import process_debug_request
            case 'banking':
                from ..subsites.banking.utils.processing import process_debug_request
            case _:
                return

        return process_debug_request(APP, path)

    if DEBUG:
        return process_debug()


@routes.after_request
def after_request(response):
    user = get_user()
    if user and not user.reflection_shown:
        user.reflection_shown = True
        commit()

    return response


@APP.errorhandler(Exception)
def handle_exception(error):
    eid = random_code()
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    name = type(error).__name__
    log('error', f"Handling app request failed ({eid}): {name}\n{tb_str}")

    if is_dev():
        return render('error_dev.html', error_id=eid,
                      name=name, error=error, traceback=tb_str)

    return render_error(eid)


@SOCKET.on('default_event')
def event_handler(data: dict | str | None):
    event = data['event']
    payload = data.get('payload')
    log('request', f"Socket event: {event} - With data: {payload}")

    def resolve_handler(event: str, subsite: str) -> callable:
        match subsite:
            case 'people':
                from ..subsites.people.socket.events import HANDLERS
            case 'learning':
                from ..subsites.learning.socket.events import HANDLERS
            case 'banking':
                from ..subsites.banking.socket.events import HANDLERS
            case _:
                from ..socket.events import HANDLERS
        return HANDLERS.get(event, no_handler)

    subsite = os.getenv('DEBUG_SUBROUTING') if DEBUG else _get_subsite()
    resolve_handler(event, subsite)(payload)


@SOCKET.on_error_default
def error_handler(error):
    eid = random_code()
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    name = type(error).__name__
    log('error', f"Handling socket event failed ({eid}): {name}\n{tb_str}")

    if is_dev():
        SOCKET.emit('error', f"Interner Server Fehler ({eid}): {name}\n{tb_str}")
        return

    SOCKET.emit('error', "Beim Ausführen der Aktion ist ein serverseitiger Fehler aufgetreten. "
                         f"(Fehler ID: {eid}) Wende dich für weitere Unterstützung bitte an "
                         "developer@growv-mail.org !")


def protect_route():
    if authenticated_user_request():
        return back_home()

    response = verify_token_ownership('captcha_token')
    if response:
        return response

    status = captcha_status()

    if status == "invalid":
        return abort(401)

    if status in {"unverified", "pending"}:
        return captcha()

    if not session.get('captcha_token_owner'):
        return render_template('auth/verify_token_ownership.html',
                               flag='verify_captcha_token')
