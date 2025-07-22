from website.routing import not_logged_in, not_allowed
from flask import Blueprint, abort
from functools import wraps

routes = Blueprint('people_routes', __name__, subdomain='people')


def require_user(strict: bool, inject_user: bool = True) -> callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from ..logic.auth import get_user
            user = get_user()
            if not user and strict:
                return abort(401)
            elif not user:
                return not_logged_in()

            return fn(user, *args, **kwargs) if inject_user else fn(*args, **kwargs)

        return wrapper
    return decorator


def require_manage_permissions(strict: bool, inject_user: bool = False) -> callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from ..logic.auth import get_user
            user = get_user()
            if not (user or user.has_manage_permissions) and strict:
                return abort(401)
            elif not user:
                return not_allowed()

            return fn(user, *args, **kwargs) if inject_user else fn(*args, **kwargs)

        return wrapper
    return decorator


def require_permissions(permissions: list[str], strict: bool, inject_user: bool = False) -> callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from ..logic.auth import get_user
            user = get_user()
            if not (user or user.has_permissions(permissions)) and strict:
                return abort(401)
            elif not user:
                return not_allowed()

            return fn(user, *args, **kwargs) if inject_user else fn(*args, **kwargs)

        return wrapper
    return decorator


def init_routes(app):
    from .site import site
    from .auth import auth
    from .user import user

    routes.register_blueprint(site)
    routes.register_blueprint(auth)
    routes.register_blueprint(user)

    app.register_blueprint(routes)
