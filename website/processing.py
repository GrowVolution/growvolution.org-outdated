from LIBRARY import *
from . import APP, DEBUG
from .socket import SOCKET, HANDLERS, no_handler
from .rendering import render_error
from .routes import auth_routes
from .logic.auth.verification import captcha_status
from .logic.auth.captcha import handle_request as captcha

def _error_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

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
    status = captcha_status()

    if status == "invalid":
        abort(401)

    if status in {"unverified", "pending"}:
        return captcha()

@APP.errorhandler(Exception)
def handle_exception(error):
    eid = _error_id()
    log('error', f"Handling app request failed ({eid}): {error}")
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
    eid = _error_id()
    log('error', f"Handling socket event failed ({eid}): {error}")
    SOCKET.emit('error', "There was an error while handling the event.")
