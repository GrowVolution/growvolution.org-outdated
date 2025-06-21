from .logic.auth.verification import get_user, is_admin, user_role
from flask import abort, flash
from functools import wraps
from typing import Callable
from LIBRARY import back_to_login, back_home


def _not_logged_in():
    flash("Du bist nicht eingeloggt.", 'warning')
    return back_to_login()


def require_user(strict: bool) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_user()
            if not user and strict:
                return abort(401)
            elif not user:
                return _not_logged_in()

            return fn(user, *args, **kwargs)

        return wrapper
    return decorator


def require_admin(strict: bool) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_user()
            if not user:
                return _not_logged_in()

            admin = is_admin()
            if not admin and strict:
                return abort(401)
            elif not admin:
                flash("Hierzu bist du nicht berechtigt!", 'danger')
                return back_home()

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def require_role(role: str, strict: bool) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_user()
            if not user:
                return _not_logged_in()

            active_role = user_role()
            denied = not active_role or active_role != role
            if denied and strict:
                return abort(401)
            elif denied:
                flash("Hierzu bist du nicht berechtigt!", 'danger')
                return back_home()

            return fn(*args, **kwargs)

        return wrapper
    return decorator
