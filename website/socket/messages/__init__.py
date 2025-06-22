from website import REDIS
from website.logic.auth import get_user
from typing import Callable
from debugger import log

MESSAGES = {}


def register_message(name: str, templates: str | list[str] | None = None) -> Callable:
    def decorator(handler):
        def wrapper(data):
            user = get_user()
            if not user:
                return

            nav_context = REDIS.get(f"nav_context:{user.id}")
            condition_2 = templates == nav_context or nav_context in templates
            if not templates or condition_2:
                handler(user, data)

        MESSAGES[name] = wrapper
        return wrapper
    return decorator


def send_message(name: str, data: dict | str | None = None):
    message = MESSAGES.get(name, None)
    message(data) if message else log('warn', f"Message function '{name}' not found.")


def init_messages():
    from . import user
