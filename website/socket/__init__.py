from . import forgot as forgot_handler, comments_and_replies as comment_system, profile as profile_handler
from flask_socketio import SocketIO
from flask import request
from typing import Callable
from debugger import log

SOCKET = SocketIO(async_mode='eventlet')
HANDLERS = {}


def register_event(name: str) -> Callable:
    def decorator(handler):
        HANDLERS[name] = handler
        return handler
    return decorator


def emit(event: str, data: dict | str | None = None, **kwargs):
    SOCKET.emit(event, data, to=request.sid, **kwargs)


def no_handler(data):
    log('warn', "Event handler not found...")
    emit('error', "Unknown event!")


def socket_flash(message: str, category: str):
    emit('flash', {'msg': message, 'cat': category})


def emit_html(html: str):
    emit('html', html)


# Forgot password
@register_event('forgot')
def forgot(data):
    forgot_handler.handle_html_request()


@register_event('reset_request')
def reset_request(data):
    forgot_handler.handle_reset_request(data)


# Comment System
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


# Profile management
@register_event('check_username')
def check_username(data):
    profile_handler.check_username(data)


@register_event('update_username')
def update_username(data):
    profile_handler.update_username(data)


@register_event('change_password')
def change_password(data):
    profile_handler.change_password(data)


@register_event('confirm_2fa')
def confirm_2fa(data):
    profile_handler.confirm_2fa(data)


@register_event('disable_2fa')
def disable_2fa(data):
    profile_handler.disable_2fa(data)


@register_event('toggle_login_notify')
def toggle_login_notify(data):
    profile_handler.toggle_login_notify(data)


@register_event('request_email_change')
def request_email_change(data):
    profile_handler.request_email_change(data)


@register_event('update_phone')
def update_phone(data):
    profile_handler.update_phone(data)


@register_event('update_address')
def update_address(data):
    profile_handler.update_address(data)


@register_event('update_birthday')
def update_birthday(data):
    profile_handler.update_birthday(data)


@register_event('update_gender')
def update_gender(data):
    profile_handler.update_gender(data)
