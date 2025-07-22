from ..routing import routes
from ..logic.auth import get_user


@routes.context_processor
def context_processor():
    return dict(
        user=get_user()
    )


@routes.before_request
def before_request():

    return None


def process_debug_request(app, path):
    response = before_request()
    if response:
        return response

    adapter = app.url_map.bind('debug.growvolution.org', subdomain='people')
    endpoint, values = adapter.match(path)
    handler = app.view_functions[endpoint]
    return handler(**values)
