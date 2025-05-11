from LIBRARY import *
from . import APP, DEBUG
from .socket import SOCKET, HANDLERS, no_handler
from .rendering import render_error, render
from .routes import auth_routes
from .logic.auth.verification import captcha_status, captcha_owner_hash, empty_token, user_role
from .logic.auth.captcha import handle_request as captcha


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


@auth_routes.before_request
def before_auth_route():
    if request.is_json and request.get_json().get('verify_captcha_token'):
        fingerprint = request.headers.get('X-Client-Fingerprint')
        owner = captcha_owner_hash() == fingerprint
        if not owner:
            return empty_token('captcha_token')

        session['captcha_token_owner'] = True
        return '', 204

    status = captcha_status()

    if status == "invalid":
        abort(401)

    if status in {"unverified", "pending"}:
        return captcha()

    if not session.get('captcha_token_owner'):
        return render_template('auth/verify_token_ownership.html')


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
def event_handler(data):
    event = data['event']
    payload = data.get('payload')
    log('request', f"Socket event: {event} - With data: {payload}")
    handler = HANDLERS.get(event, no_handler)
    handler(payload)


@SOCKET.on_error_default
def error_handler(error):
    eid = random_code()
    log('error', f"Handling socket event failed ({eid}): {repr(error)}")
    SOCKET.emit('error', "There was an error while handling the event.")
