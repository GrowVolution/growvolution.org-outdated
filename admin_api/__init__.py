from shared.debugger import start_session, log
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from dotenv import load_dotenv
from pathlib import Path
import warnings, os, signal, eventlet

warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")

APP = Flask(__name__)
APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=1, x_proto=1, x_host=1)
LIMITER = Limiter(get_remote_address, default_limits=["500 per day", "100 per hour"])
SOCKET = SocketIO(async_mode='eventlet')


def _on_shutdown(signum, frame):
    log('info', f"Handling signal {signal.Signals(signum).name}, shutting down...")

    def do_shutdown():
        from .utils.site_control import stop_main, stop_worker
        stop_main()
        stop_worker()

        if not APP.config['SANDBOX_MODE']:
            from .data import DATABASE
            from .utils import execute
            from .utils.dev_containers import stop_container
            from shared.data import delete_model

            with APP.app_context():
                note_db = DATABASE.resolve('dev_note')
                for note in note_db.query.all():
                    port = 6000 + note.uid
                    execute(
                        ["bash", "-c", f"lsof -ti :{port} | xargs --no-run-if-empty kill -15"],
                        privileged=True
                    ).wait()
                    stop_container(note.user.name)
                    delete_model(note)

        SOCKET.stop()

    eventlet.spawn_n(do_shutdown)


def _production_init(db_manage):
    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)

    with open('/root/.psw/db_system.txt', 'r') as file:
        db_system_pw = file.read().strip()

    db_user = os.getenv("DB_USER").format(password=db_system_pw)
    db_base = os.getenv("DB_BASE_URI")
    APP.config['SQLALCHEMY_DATABASE_URI'] = db_base.format(user=db_user, database='AccessControl')

    if db_manage:
        return

    with open('/root/.psw/fernet.txt', 'r') as file:
        APP.config['FERNET_KEY'] = file.read().strip()


def _sandbox_init(db_manage):
    APP.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
    if db_manage:
        return
    APP.config['FERNET_KEY'] = os.getenv("FERNET_KEY")


def init_app(db_manage: bool = False):
    sandbox_mode = os.getenv("SANDBOX_MODE") == "TRUE"

    if sandbox_mode:
        _sandbox_init(db_manage)
    else:
        _production_init(db_manage)

    from shared.data import DB, BCRYPT, MIGRATE
    from .data import DATABASE

    DB.init_app(APP)
    BCRYPT.init_app(APP)
    MIGRATE.init_app(APP, DB)
    DATABASE.initialize()

    if db_manage:
        return

    APP.config['SANDBOX_MODE'] = sandbox_mode
    APP.config['SERVER_NAME'] = os.getenv("SERVER_NAME")
    APP.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    LIMITER.init_app(APP)
    SOCKET.init_app(APP)

    os.environ['INSTANCE'] = 'Admin API'
    start_session()

    with APP.app_context():
        env = DATABASE.resolve('env')
        APP.config['NRS_PASSWORD'] = env.query.get('NRS_PASSWORD').value

    from shared.mail_service import start
    start(APP, True)

    from .api import API
    API.initialize()

    from .system import SYSTEM
    SYSTEM.initialize()
    clear = SYSTEM.resolve('clear_logs')
    clear()


    from .utils.data_control import update_api_db, update_site_db
    update_api_db()
    update_site_db()

    from .utils.site_control import start_main, start_worker
    start_main()
    #start_worker() // currently not needed

    from .utils import processing, update_debug_routing
    update_debug_routing()

    signal.signal(signal.SIGINT, _on_shutdown)
    signal.signal(signal.SIGTERM, _on_shutdown)
