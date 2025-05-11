from LIBRARY import *

warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")

APP = Flask(__name__)
APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=3, x_proto=1, x_host=1)
LIMITER = Limiter(get_remote_address, default_limits=["500 per day", "100 per hour"])

DEBUG = False


def init_app():
    global DEBUG

    APP.config['EXEC_MODE'] = os.getenv("EXEC_MODE")
    DEBUG = os.getenv("INSTANCE") == 'debug'

    APP.config['NRS_PASSWORD'] = os.getenv("NRS_PASSWORD")

    APP.config['SERVER_NAME'] = os.getenv("SERVER_NAME")
    APP.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    APP.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
    APP.config['RATELIMIT_STORAGE_URL'] = os.getenv("LIMITER")
    LIMITER.init_app(APP)

    import website.processing

    from .routes import routes, auth_routes

    APP.register_blueprint(routes)
    APP.register_blueprint(auth_routes)

    from .data import DB, BCRYPT
    DB.init_app(APP)
    BCRYPT.init_app(APP)

    from .socket import SOCKET
    SOCKET.init_app(APP)

    from debugger import start_session
    start_session()

    from mail_service import start
    start(APP)
