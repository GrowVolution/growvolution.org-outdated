from flask import abort, flash, Response, redirect, Blueprint
from functools import wraps


class Methods:
    DEFAULT = ['GET']
    POST = ['POST']
    ALL = ['GET', 'POST']

METHODS = Methods()

routes = Blueprint('routes', __name__)


def register_blueprints(app):
    from .site import site
    from .auth import auth
    from .api import api
    from .blog import blog
    from .user import user, init_routes
    init_routes()

    routes.register_blueprint(site)
    routes.register_blueprint(auth)
    routes.register_blueprint(user)
    routes.register_blueprint(api, url_prefix='/api')
    routes.register_blueprint(blog, url_prefix='/blog')

    app.register_blueprint(routes)


def back_home() -> Response:
    return redirect('/')


def back_to_login() -> Response:
    return redirect('/login')


def not_logged_in():
    flash("Du bist nicht eingeloggt.", 'warning')
    return back_to_login()


def not_allowed():
    flash("Hierzu bist du nicht berechtigt!", 'danger')
    return back_home()


def require_user(strict: bool, inject_user: bool = True) -> callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from website.logic.auth import get_user
            user = get_user()
            if not user and strict:
                return abort(401)
            elif not user:
                return not_logged_in()

            return fn(user, *args, **kwargs) if inject_user else fn(*args, **kwargs)

        return wrapper
    return decorator


def require_admin(strict: bool, inject_user: bool = False) -> callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from website.logic.auth import get_user
            user = get_user()
            if not user:
                return not_logged_in()

            admin = user.role == 'admin'
            if not admin and strict:
                return abort(401)
            elif not admin:
                return not_allowed()

            return fn(user, *args, **kwargs) if inject_user else fn(*args, **kwargs)

        return wrapper
    return decorator


def require_role(role: str, strict: bool, inject_user: bool = False) -> callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from website.logic.auth import get_user
            user = get_user()
            if not user:
                return not_logged_in()

            active_role = user.role
            denied = not active_role or active_role != role
            if denied and strict:
                return abort(401)
            elif denied:
                return not_allowed()

            return fn(user, *args, **kwargs) if inject_user else fn(*args, **kwargs)

        return wrapper
    return decorator
