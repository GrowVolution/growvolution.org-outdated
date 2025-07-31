from .. import APP
from ..data import DATABASE
from shared.packaging import Package
from root_dir import ROOT_PATH

from cryptography.fernet import Fernet
from collections import deque
from pathlib import Path
import subprocess, os

UTILS = Package(Path(__file__).parent)

LOG_DIR = ROOT_PATH / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

_prod_env = {}

_backend_template = """
    location /{name}/ {{
        proxy_pass http://localhost:{port}/;
        include proxy_params;
        include upgrade_params;
        
        error_page 502 504 = @backend_down;
    }}
"""

unix_param = "?unix_socket=/var/run/mysqld/mysqld.sock"


@UTILS.register('get_fernet')
def get_fernet():
    key = APP.config['FERNET_KEY']
    return Fernet(key)


@UTILS.register('encrypt')
def fernet_encrypted(data: bytes) -> str:
    return get_fernet().encrypt(data).decode()


@UTILS.register('decrypt')
def fernet_decrypted(data: bytes) -> str:
    return get_fernet().decrypt(data).decode()


def _exec_unprivileged(args: list[str], **kwargs):
    cmd = ['sudo', '-u', 'admin']
    env = kwargs.pop('env', None)

    if env:
        env_args = [f'{k}={v}' for k, v in env.items()]
        cmd += ['env'] + env_args

    cmd += args
    return subprocess.Popen(cmd, shell=False, **kwargs)


def _exec_privileged(args: list[str], **kwargs):
    return subprocess.Popen(args, shell=False, **kwargs)


@UTILS.register('exec')
def execute(args: list[str], **kwargs):
    privileged = kwargs.pop('privileged', False)
    return_as_result = kwargs.pop('return_as_result', False)
    if return_as_result:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.STDOUT
        kwargs['text'] = True

    exec_fn = _exec_privileged if privileged else _exec_unprivileged
    proc = exec_fn(args, **kwargs)
    if return_as_result:
        output = proc.communicate()[0]
        return output, proc.returncode

    return proc


def _get_latest_file(folder):
    files = [f for f in folder.iterdir() if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def _tail(file, lines=100):
    with open(file, 'r') as f:
        return list(deque(f, maxlen=lines))


@UTILS.register('latest_log')
def get_latest_log(name: str = None):
    folder = LOG_DIR / name if name else LOG_DIR
    file = _get_latest_file(folder)
    return _tail(file) if file else None


def _site_db_uri():
    sandbox = APP.config['SANDBOX_MODE']
    with open(f"/root/.psw/db_{'sandbox' if sandbox else 'system'}.txt", 'r') as file:
        db_pw = file.read().strip()

    db_user = os.getenv("DB_USER").format(password=db_pw)
    db_base = os.getenv("DB_BASE_URI")
    return db_base.format(user=db_user, database=f'SiteSandbox{unix_param}' if sandbox else 'GrowVolution')


@UTILS.register('load_env')
def load_env(reload: bool = False):
    global _prod_env
    if _prod_env and not reload:
        return _prod_env

    with APP.app_context():
        group_db = DATABASE.resolve('env_group')
        prod_group = group_db.query.filter_by(production=True).first()
        _prod_env = { e.key: e.value for e in prod_group.vars }
        _prod_env['DB_URI'] = _site_db_uri()
        return _prod_env


@UTILS.register('update_backends')
def update_debug_routing():
    with APP.app_context():
        admin_db = DATABASE.resolve('admin')
        admins = admin_db.query.all()

    api_backends = [_backend_template.format(
        name=user.name,
        port=6000 + user.id
    ) for user in admins]
    with open('/etc/nginx/api_backends', 'w') as file:
        file.write('\n\n'.join(api_backends))

    site_backends = [_backend_template.format(
        name=user.name,
        port=7000 + user.id
    ) for user in admins]
    with open('/etc/nginx/site_backends', 'w') as file:
        file.write('\n\n'.join(site_backends))

    subprocess.run(['systemctl', 'restart', 'nginx'], check=True)
