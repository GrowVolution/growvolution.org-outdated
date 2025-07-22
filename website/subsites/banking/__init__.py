

def init_site(app):
    from .utils import processing
    from .routing import init_routes
    from .socket import init_socket

    init_routes(app)
    init_socket()
