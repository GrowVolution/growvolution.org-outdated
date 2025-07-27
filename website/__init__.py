from shared.debugger import log, start_session
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlparse
from jinja2 import ChoiceLoader, PrefixLoader, FileSystemLoader
from root_dir import ROOT_PATH
from types import FrameType
import warnings, os, redis, signal

warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")

APP = Flask(__name__)
APP.subdomain_matching = True
APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=1, x_proto=1, x_host=1)
LIMITER = Limiter(get_remote_address, default_limits=["500 per day", "100 per hour"])

APP.jinja_loader = ChoiceLoader([
    PrefixLoader({
        'main': FileSystemLoader('website/templates'),
        'banking': FileSystemLoader('website/subsites/banking/templates'),
        'learning': FileSystemLoader('website/subsites/learning/templates'),
        'people': FileSystemLoader('website/subsites/people/templates')
    }),
    FileSystemLoader('website/templates')
])

REDIS_URL = urlparse(os.getenv("REDIS_URI"))
REDIS = redis.Redis(
    host=REDIS_URL.hostname,
    port=REDIS_URL.port,
    password=REDIS_URL.password,
    decode_responses=True,
    db=1
)

DEBUG = False


def _on_shutdown(signum: int, frame: FrameType | None):
    log('info', f"""Handling signal {
        'SIGTERM' if signum == signal.SIGTERM else 'SIGINT'
    }, shutting down...""")

    from .socket import SOCKET
    SOCKET.stop()


def init_app(db_manage: bool = False):
    APP.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

    from shared.data import DB, BCRYPT, MIGRATE
    from .data import init_models

    DB.init_app(APP)
    BCRYPT.init_app(APP)
    MIGRATE.init_app(APP, DB)
    init_models(APP)

    if db_manage:
        return

    global DEBUG
    DEBUG = os.getenv("INSTANCE") == 'debug'

    APP.config['NRS_PASSWORD'] = os.getenv("NRS_PASSWORD")
    APP.config['SERVER_NAME'] = os.getenv("SERVER_NAME")
    APP.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    APP.config['RATELIMIT_STORAGE_URL'] = os.getenv("REDIS_URI")
    LIMITER.init_app(APP)

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(
        ROOT_PATH / 'website' / 'auth' / 'google-service-key.json'
    )

    import website.utils.processing
    from .routing import register_blueprints
    register_blueprints(APP)

    from .socket import SOCKET, init_socket
    SOCKET.init_app(APP)
    init_socket()

    start_session()

    from shared.mail_service import start
    start(APP)

    from .subsites import init_subsites
    init_subsites(APP)

    from .easteregg import init_easteregg
    init_easteregg(APP)

    signal.signal(signal.SIGINT, _on_shutdown)
    signal.signal(signal.SIGTERM, _on_shutdown)
