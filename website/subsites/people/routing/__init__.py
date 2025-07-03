from flask import Blueprint

routes = Blueprint('people_routes', __name__, subdomain='people')


def init_routes(app):
    from .site import site

    routes.register_blueprint(site)

    app.register_blueprint(routes)
