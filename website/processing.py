from . import APP, DEBUG
from .socket import SOCKET, HANDLERS, no_handler
from .rendering import render_error, render
from .routes import auth_routes
from .logic.auth.verification import captcha_status, token_owner_hash, empty_token, user_role, authenticated_user_request
from .logic.auth.captcha import handle_request as captcha
from flask import Response, request, abort, render_template, make_response, session
from LIBRARY import back_home, random_code
from debugger import log


def _verify_token_ownership(name: str = 'token') -> Response | None:
    if request.is_json and request.get_json().get(f'verify_{name}'):
        fingerprint = request.headers.get('X-Client-Fingerprint')
        owner = token_owner_hash(name) == fingerprint
        if not owner:
            return empty_token(name)

        session[f'{name}_owner'] = True
        return make_response('', 204)

    return None


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

    log('request', f"{method} '{path}'{''.join(' ' for _ in range(32 - len(path)))} "
                   f"from {ip}{''.join(' ' for _ in range(15 - len(ip)))} via ({agent}).")

    response = _verify_token_ownership()
    if response:
        return response

    if authenticated_user_request() and not session.get("token_owner"):
        return render_template('auth/verify_token_ownership.html',
                               flag='verify_token')


@auth_routes.before_request
def before_auth_route():
    if authenticated_user_request() and not request.path == '/logout':
        return back_home()

    response = _verify_token_ownership('captcha_token')
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


@APP.errorhandler(Exception)
def handle_exception(error):
    eid = random_code()
    log('error', f"Handling app request failed ({eid}): {repr(error)}")

    if user_role() == 'dev':
        import sys, traceback
        tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
        return render('error_dev.html', error_id=eid,
                      name=type(error).__name__, error=error,
                      traceback=tb_str)

    return render_error(eid)


@SOCKET.on('default_event')
def event_handler(data: dict):
    event = data['event']
    payload = data.get('payload')
    log('request', f"Socket event: {event} - With data: {payload}")
    handler = HANDLERS.get(event, no_handler)
    handler(payload)


@SOCKET.on_error_default
def error_handler(error):
    eid = random_code()
    log('error', f"Handling socket event failed ({eid}): {repr(error)}")

    if user_role() == 'dev':
        import sys, traceback
        tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
        SOCKET.emit('error', f"Interner Server Fehler ({eid}): {repr(error)}\n{tb_str}")
        return

    SOCKET.emit('error', "Beim Ausführen der Aktion ist ein serverseitiger Fehler aufgetreten. "
                         f"(Fehler ID: {eid}) Wende dich für weitere Unterstützung bitte an "
                         "developer@growv-mail.org !")
