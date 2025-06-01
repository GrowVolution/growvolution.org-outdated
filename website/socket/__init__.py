from . import forgot as forgot_handler, comments_and_replies as comment_system
from flask_socketio import SocketIO
from typing import Callable
from debugger import log

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


@register_event('add_comment')
def add_comment(data):
    comment_system.handle_comment(data)


@register_event('add_reply')
def add_reply(data):
    comment_system.handle_reply(data)


@register_event('add_like')
def add_like(data):
    comment_system.handle_like(data)


@register_event('remove_like')
def remove_like(data):
    comment_system.handle_unlike(data)


@register_event('comment_system_edit')
def handle_edit(data):
    comment_system.handle_edit(data)


@register_event('comment_system_delete')
def handle_delete(data):
    comment_system.handle_delete(data)


@register_event('reply_request')
def reply_request(data):
    comment_system.handle_reply_request(data)
