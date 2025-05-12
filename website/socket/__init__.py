from LIBRARY import *
from . import forgot as forgot_handler

SOCKET = SocketIO(async_mode='eventlet')
HANDLERS = {}


def register_event(name: str) -> Callable:
    def decorator(handler):
        HANDLERS[name] = handler
        return handler
    return decorator


def no_handler(data):
    log('warn', "Event handler not found...")
    SOCKET.emit('error', "Unknown event!")


def socket_flash(message: str, category: str):
    SOCKET.emit('flash', {'msg': message, 'cat': category})


def emit_html(html: str):
    SOCKET.emit('html', html)


# Forgot password events
@register_event('forgot')
def forgot(data):
    forgot_handler.handle_html_request()


@register_event('reset_request')
def reset_request(data):
    forgot_handler.handle_reset_request(data)