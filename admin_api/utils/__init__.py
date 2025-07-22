from .. import APP
from ..data import DATABASE
from root_dir import ROOT_PATH
from cryptography.fernet import Fernet
from collections import deque
import subprocess, os

LOG_DIR = ROOT_PATH / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

_prod_env = {}


def get_fernet():
    key = APP.config['FERNET_KEY']
    return Fernet(key)


def fernet_encrypted(data: bytes) -> str:
    return get_fernet().encrypt(data).decode()


def fernet_decrypted(data: bytes) -> str:
    return get_fernet().decrypt(data).decode()


def verify_system_id(identifier: str):
    from ..data.environment import Environment
    var = Environment.query.get('SYSTEM_ID')
    return var and var.value == identifier


def exec_unprivileged(args: list[str], **kwargs):
    cmd = ['sudo', '-u', 'growvolution']
    env = kwargs.pop('env', None)

    if env:
        env_args = [f'{k}={v}' for k, v in env.items()]
        cmd += ['env'] + env_args

    cmd += args
    return subprocess.Popen(cmd, shell=False, **kwargs)


def exec_privileged(args: list[str], **kwargs):
    return subprocess.Popen(args, shell=False, **kwargs)


def _get_latest_file(folder):
    files = [f for f in folder.iterdir() if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def _tail(file, lines=100):
    with open(file, 'r') as f:
        return list(deque(f, maxlen=lines))


def get_latest_log(name: str = None):
    folder = LOG_DIR / name if name else LOG_DIR
    file = _get_latest_file(folder)
    return _tail(file) if file else None


def _production_db_uri():
    with open('/root/.psw/db_system.txt', 'r', encoding='utf-8') as file:
        db_system_pw = file.read().strip()

    db_user = os.getenv("DB_USER").format(password=db_system_pw)
    db_base = os.getenv("DB_BASE_URI")
    return db_base.format(user=db_user, database='GrowVolution')


def load_env(reload: bool = False):
    global _prod_env
    if _prod_env and not reload:
        return _prod_env

    env_db = DATABASE.resolve('env')
    _prod_env = { e.key: e.value for e in env_db.query.all() }
    _prod_env['DB_URI'] = _production_db_uri()
    return _prod_env
