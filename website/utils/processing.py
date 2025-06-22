from . import random_code
from .. import APP, DEBUG
from ..socket import SOCKET
from ..socket.events import HANDLERS, no_handler
from .rendering import render_error, render
from ..logic.auth import (captcha_status, verify_token_ownership, user_role,
                          authenticated_user_request, twofa_status)
from ..logic.auth.captcha import handle_request as captcha
from ..logic.auth.twofa import handle_2fa
from ..routing import back_home
from flask import request, abort, render_template, session
from debugger import log
import sys, traceback


@APP.context_processor
def context_processor():
    return dict(
        debug=DEBUG,
    )


@APP.before_request
def before_request():
    method = request.method.upper()
    path = request.path
    ip = request.remote_addr
    agent = request.headers.get('User-Agent')
    agent = agent if agent else 'no-agent'

    log('request', f"{method} '{path:48}' from {ip:15} via ({agent}).")

    response = verify_token_ownership()
    if response:
        return response

    safe_path = path.startswith('/static') or path.startswith('/socket.io')
    response = handle_2fa() if not safe_path else None
    if response:
        return response

    if authenticated_user_request() and not session.get("token_owner"):
        return render_template('auth/verify_token_ownership.html',
                               flag='verify_token')


@APP.errorhandler(Exception)
def handle_exception(error):
    eid = random_code()
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    name = type(error).__name__
    log('error', f"Handling app request failed ({eid}): {name}\n{tb_str}")

    if user_role() == 'dev':
        return render('error_dev.html', error_id=eid,
                      name=name, error=error, traceback=tb_str)

    return render_error(eid)


@SOCKET.on('default_event')
def event_handler(data: dict | str | None):
    event = data['event']
    payload = data.get('payload')
    log('request', f"Socket event: {event} - With data: {payload}")
    handler = HANDLERS.get(event, no_handler)
    handler(payload)


@SOCKET.on_error_default
def error_handler(error):
    eid = random_code()
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    name = type(error).__name__
    log('error', f"Handling socket event failed ({eid}): {name}\n{tb_str}")

    if user_role() == 'dev':
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
        abort(401)

    if status in {"unverified", "pending"}:
        return captcha()

    if not session.get('captcha_token_owner'):
        return render_template('auth/verify_token_ownership.html',
                               flag='verify_captcha_token')
