from .. import SOCKET, socket_flash, emit
from website import REDIS
from website.logic.auth import get_user
from typing import TYPE_CHECKING
from flask import request
from shared.debugger import log

if TYPE_CHECKING:
    from website.data.user import User

HANDLERS = {}


def register_event(name: str) -> callable:
    def decorator(handler):
        HANDLERS[name] = handler
        return handler
    return decorator


def no_handler(data):
    log('warn', "Event handler not found...")
    emit('error', "Unknown event!")


def require_user(strict: bool):
    def decorator(fn):
        def wrapper(data=None):
            user = get_user()
            if user:
                fn(user, data) if data else fn(user)
            elif strict:
                socket_flash("Nicht authentifiziert!", "danger")
        return wrapper
    return decorator


@SOCKET.on('connect')
@require_user(False)
def on_connect(user: 'User'):
    REDIS.set(f"user_sid:{user.id}", request.sid)


@SOCKET.on('disconnect')
@require_user(False)
def on_disconnect(user: 'User', disconnect_info):
    REDIS.delete(f"user_sid:{user.id}")
    REDIS.delete(f"nav_context:{user.id}")


@register_event('set_nav_context')
@require_user(False)
def set_nav_context(user: 'User', template_name: str):
    REDIS.set(f"nav_context:{user.id}", template_name)


def init_events():
    from . import forgot, profile, comment_system, week
