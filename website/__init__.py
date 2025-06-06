from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import warnings, os

warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")

APP = Flask(__name__)
APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=3, x_proto=1, x_host=1)
LIMITER = Limiter(get_remote_address, default_limits=["500 per day", "100 per hour"])

DEBUG = False


def init_app(db_manage: bool = False):
    global DEBUG

    APP.config['EXEC_MODE'] = os.getenv("EXEC_MODE")
    DEBUG = os.getenv("INSTANCE") == 'debug'

    APP.config['NRS_PASSWORD'] = os.getenv("NRS_PASSWORD")
    APP.config['SERVER_NAME'] = os.getenv("SERVER_NAME")
    APP.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    APP.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
    APP.config['RATELIMIT_STORAGE_URL'] = os.getenv("LIMITER")

    from .data import DB, BCRYPT, MIGRATE, init_models

    DB.init_app(APP)
    BCRYPT.init_app(APP)
    MIGRATE.init_app(APP, DB)
    init_models()

    if db_manage:
        return

    LIMITER.init_app(APP)

    import website.processing
    from .routes import routes
    from .auth_routes import auth_routes
    from .api_routes import api_routes
    APP.register_blueprint(routes)
    APP.register_blueprint(auth_routes)
    APP.register_blueprint(api_routes, url_prefix='/api')

    from .socket import SOCKET
    SOCKET.init_app(APP)

    from debugger import start_session
    start_session()

    from mail_service import start
    start(APP)
