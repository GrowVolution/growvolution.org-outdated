from LIBRARY import *
from .rendering import render, render_404
from .logic.auth import login as login_handler, google_auth, apple_auth, microsoft_auth

routes = Blueprint('routes', __name__)
auth_routes = Blueprint('auth_routes', __name__)

# Main Routes
@routes.route('/')
def index():
    return render("site/home.html")

# Authentication routes
@auth_routes.route('/login', methods=METHOD.all)
def login():
    return login_handler.handle_request()

@auth_routes.route('/oauth/<api>/start')
def start_oauth(api):
    return google_auth.start_oauth() if api == 'google' else (
        apple_auth.start_oauth() if api == 'apple' else (
            microsoft_auth.start_oauth() if api == 'microsoft' else render_404()
        )
    )

@routes.route('/oauth/<api>/callback', methods=METHOD.all)
def oauth_callback(api):
    return google_auth.oauth_callback() if api == 'google' else (
        apple_auth.oauth_callback() if api == 'apple' else (
            microsoft_auth.oauth_callback() if api == 'microsoft' else render_404()
        )
    )

# Legal Routes
@routes.route('/about')
def about():
    return render("site/about.html")

@routes.route('/privacy')
def privacy():
    return render("site/privacy.html")

@routes.route('/guidelines')
def guidelines():
    return render("site/guidelines.html")

@routes.route('/impressum')
def impressum():
    return render("site/impressum.html")

# Not Found
@routes.route('/<path:path>')
def not_found(path):
    return render_404()

# Processing debug requests for testing
@routes.route('/debug')
def debug():
    """

        TODO: Debug Stuff

    """
    return back_home()