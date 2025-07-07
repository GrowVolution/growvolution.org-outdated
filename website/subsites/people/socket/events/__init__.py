from typing import Callable

HANDLERS = {}


def register_event(name: str) -> Callable:
    def decorator(handler):
        HANDLERS[name] = handler
        return handler
    return decorator


@register_event("set_nav_context")
def set_nav_context(template: str):
    pass


def init_events():
    pass
