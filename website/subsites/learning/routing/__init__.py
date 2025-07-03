from flask import Blueprint

routes = Blueprint('learning_routes', __name__, subdomain='learning')


def init_routes(app):
    from .site import site

    routes.register_blueprint(site)

    app.register_blueprint(routes)
