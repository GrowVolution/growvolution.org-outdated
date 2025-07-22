from shared.debugger import start_session, log
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from dotenv import load_dotenv
from pathlib import Path
from types import FrameType
import warnings, os, signal

warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")

APP = Flask(__name__)
APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=1, x_proto=1, x_host=1)
LIMITER = Limiter(get_remote_address, default_limits=["500 per day", "100 per hour"])
SOCKET = SocketIO(async_mode='eventlet')


def _on_shutdown(signum: int, frame: FrameType | None):
    log('info', f"""Handling signal {
        'SIGTERM' if signum == signal.SIGTERM else 'SIGINT'
    }, shutting down...""")

    from .utils.server_control import stop_main, stop_worker
    stop_main()
    stop_worker()
    SOCKET.stop()


def init_app(db_manage: bool = False):
    from main import BASE_ENV
    print(BASE_ENV)

    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)

    APP.config['SERVER_NAME'] = os.getenv("SERVER_NAME")
    APP.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    with open('/root/.psw/db_system.txt', 'r', encoding='utf-8') as file:
        db_system_pw = file.read().strip()

    db_user = os.getenv("DB_USER").format(password=db_system_pw)
    db_base = os.getenv("DB_BASE_URI")
    APP.config['SQLALCHEMY_DATABASE_URI'] = db_base.format(user=db_user, database='AccessControl')

    from shared.data import DB, BCRYPT, MIGRATE
    from .data import DATABASE

    DB.init_app(APP)
    BCRYPT.init_app(APP)
    MIGRATE.init_app(APP, DB)
    DATABASE.initialize()

    if db_manage:
        return

    with open('/root/.psw/fernet.txt', 'r', encoding='utf-8') as file:
        APP.config['FERNET_KEY'] = file.read().strip()

    LIMITER.init_app(APP)
    SOCKET.init_app(APP)

    os.environ['INSTANCE'] = 'Admin API'
    start_session()

    with APP.app_context():
        env = DATABASE.resolve('env')
        APP.config['NRS_PASSWORD'] = env.query.get('NRS_PASSWORD').value

        from .utils.server_control import start_main, start_worker
        start_main()
        #start_worker() // currently not needed

    from shared.mail_service import start
    start(APP, True)

    from .api import API
    API.initialize()

    from .system import SYSTEM
    SYSTEM.initialize()

    from .utils import processing

    signal.signal(signal.SIGINT, _on_shutdown)
    signal.signal(signal.SIGTERM, _on_shutdown)
