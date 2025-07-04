from typing import Callable

HANDLERS = {}


def register_event(name: str) -> Callable:
    def decorator(handler):
        HANDLERS[name] = handler
        return handler
    return decorator


def init_events():
    pass
