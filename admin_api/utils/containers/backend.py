from . import CLIENT, IMAGE_NAME, SANDBOX_DIR, PROJECT_PATH_STR
from .. import UTILS, unix_param
from ... import APP
from ...data import DATABASE
from shared.data import delete_model
from shared.debugger import log
from root_dir import ROOT_PATH

import os

_env = {}
_observer = None

get_container = UTILS.resolve('docker_container')

def _get_port(name):
    admins = DATABASE.resolve('admin')
    user = admins.query.filter_by(name=name).first()
    if not user:
        raise ValueError(f"The given user '{name}' does not exist.")

    return 6000 + user.id


def _load_env():
    global _env
    if _env:
        return _env

    _env['SANDBOX_MODE'] = "true"

    with open('/root/.psw/db_sandbox.txt', 'r') as file:
        sandbox_psw = file.read().strip()

    db_user = f"sandbox:{sandbox_psw}"
    db_base = os.getenv("DB_BASE_URI")
    _env['DB_URI'] = db_base.format(user=db_user, database=f'ApiSandbox{unix_param}')

    return _env


def _observe():
    global _observer
    if _observer:
        return

    def reload():
        container_exec = UTILS.resolve('container_exec')

        with APP.app_context():
            note_db = DATABASE.resolve('dev_note')
            for note in note_db.query.all():
                container_name = f"{note.user.name}_backend"
                container = get_container(container_name)
                if not container:
                    delete_model(note)
                    continue

                container_exec(container_name,
                               ["bash", "-c", "lsof -ti :5001 | xargs --no-run-if-empty kill -15 || true ; "
                                              "lsof -ti :5000 | xargs --no-run-if-empty kill -1 || true"])

    watcher = UTILS.resolve('watcher')
    handler = watcher(reload)

    start_watcher = UTILS.resolve('watch_sandbox')
    _observer = start_watcher(handler)


@UTILS.register('start_dev_backend')
def start_container(name: str, env_group: str):
    container_name = f"{name}s_backend"
    if get_container(container_name):
        log('warn', f"Container {container_name} already running.")
        return

    groups = DATABASE.resolve('env_group')
    group = groups.query.filter_by(name=env_group).first()
    if not group:
        raise ValueError(f"The given group '{env_group}' does not exist.")
    elif group.production:
        raise PermissionError(f"Running sandbox with the production environment is not allowed.")

    env = _load_env()
    for var in group.vars:
        env[var.key] = var.value

    auth = str(ROOT_PATH / "website" / "auth")
    sock_path = unix_param.split('=')[1]
    sock_dir = os.path.dirname(sock_path)

    port = _get_port(name)

    CLIENT.containers.run(
        IMAGE_NAME,
        name=container_name,
        detach=True,
        ports={
            "5000/tcp": port,
            "5001/tcp": port + 1000,
        },
        volumes={
            str(SANDBOX_DIR): {"bind": PROJECT_PATH_STR, "mode": "rw"},
            auth: {"bind": f"{PROJECT_PATH_STR}/website/auth", "mode": "ro"},
            sock_dir: {"bind": sock_dir, "mode": "ro"},
        },
        environment=env,
        command=[
            "/bin/bash", "-c",
            "sudo -u admin sh -c 'pip install --upgrade pip && "
            f"pip install -r {PROJECT_PATH_STR}/requirements.txt' && "
            f"python {PROJECT_PATH_STR}/main.py"
        ],
        user="root"
    )

    _observe()


@UTILS.register('stop_dev_backend')
def stop_container(name: str, skip_check: bool = False):
    stop = UTILS.resolve('stop_container')
    stop(f"{name}s_backend")

    if skip_check:
        return

    global _observer
    note_db = DATABASE.resolve('dev_note')
    if note_db.query.count() == 0 and _observer:
        stop_watcher = UTILS.resolve('unwatch_sandbox')
        stop_watcher(_observer)
        _observer = None
