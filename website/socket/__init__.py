from website import REDIS
from flask_socketio import SocketIO
from flask import request
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from website.data.user import User

SOCKET = SocketIO(async_mode='eventlet')


def emit(event: str, data: dict | str | None = None, to_user: Optional['User'] = None, **kwargs):
    sid = REDIS.get(f"user_sid:{to_user.id}") if to_user else None
    SOCKET.emit(event, data, to=sid if sid else request.sid, **kwargs)


def socket_flash(message: str, category: str):
    emit('flash', {'msg': message, 'cat': category})


def emit_html(html: str):
    emit('html', html)


def init_socket():
    from .events import init_events
    from .messages import init_messages
    init_events()
    init_messages()
