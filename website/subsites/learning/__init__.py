

def init_site(app):
    from .utils import processing
    from .routing import init_routes

    init_routes(app)
