from flask import abort, flash, Response, redirect
from functools import wraps
from typing import Callable


class Methods:
    DEFAULT = ['GET']
    POST = ['POST']
    ALL = ['GET', 'POST']

METHODS = Methods()


def register_blueprints(app):
    from .site import site
    from .auth import auth
    from .user import user
    from .api import api
    from .blog import blog

    app.register_blueprint(site)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(blog, url_prefix='/blog')


def back_home() -> Response:
    return redirect('/')


def back_to_login() -> Response:
    return redirect('/login')


def _not_logged_in():
    flash("Du bist nicht eingeloggt.", 'warning')
    return back_to_login()


def require_user(strict: bool) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from website.logic.auth import get_user
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
            from website.logic.auth import get_user, is_admin
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
            from website.logic.auth import get_user, user_role
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
