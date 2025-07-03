from flask import Blueprint

routes = Blueprint('banking_routes', __name__, subdomain='banking')


def init_routes(app):
    from .site import site

    routes.register_blueprint(site)

    app.register_blueprint(routes)
