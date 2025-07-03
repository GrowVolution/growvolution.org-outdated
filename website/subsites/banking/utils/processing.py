from ..routing import routes


@routes.before_request
def before_request():

    return None


def process_debug_request(app, path):
    response = before_request()
    if response:
        return response

    adapter = app.url_map.bind('debug.growvolution.org', subdomain='banking')
    endpoint, values = adapter.match(path)
    handler = app.view_functions[endpoint]
    return handler(**values)
