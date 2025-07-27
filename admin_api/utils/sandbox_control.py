from . import execute
from .watcher import Handler, start_watcher, stop_watcher
from .dev_containers import SANDBOX_DIR
from ..data import DATABASE
from root_dir import ROOT_PATH
from git import Repo, GitCommandError
import os

_env = {
    'SANDBOX_MODE': 'true',
}

_observer = None


def _load_env():
    global _env
    if _env:
        return _env

    _env['SANDBOX_MODE'] = "TRUE"

    with open('/root/.psw/db_sandbox.txt', 'r') as file:
        sandbox_psw = file.read().strip()

    db_user = os.getenv("DB_USER").format(password=sandbox_psw)
    db_base = os.getenv("DB_BASE_URI")
    _env['DB_URI'] = db_base.format(user=db_user, database='ApiSandbox')

    return _env


def _get_port(name):
    admins = DATABASE.resolve('admin')
    user = admins.query.filter_by(name=name).first()
    if not user:
        raise ValueError(f"The given user '{name}' does not exist.")

    return 6000 + user.id


def create_debug_process(name: str, env_group: str):
    groups = DATABASE.resolve('env_group')
    group = groups.query.filter_by(name=env_group).first()
    if not group:
        raise ValueError(f"The given group '{env_group}' does not exist.")
    elif group.production:
        raise PermissionError(f"Running sandbox with the production environment is not allowed.")

    stop_debug_process(name, True)

    env = _load_env()
    for var in group.vars:
        env[var.key] = var.value

    env['PORT'] = _get_port(name)

    venv = SANDBOX_DIR / ".venv"
    if not venv.exists():
        execute(
            ['ln', '-s', ROOT_PATH / '.venv', venv],
            privileged=True
        )

    execute(
        ['bash', SANDBOX_DIR / "run.sh"],
        env=env
    )

    observe()


def stop_debug_process(name: str, skip_check: bool = False):
    port = _get_port(name)
    execute(
        ["bash", "-c", f"lsof -ti :{port} | xargs --no-run-if-empty kill -15"],
        privileged=True
    )

    if skip_check:
        return

    global _observer
    note_db = DATABASE.resolve('dev_note')
    if note_db.query.count() == 0 and _observer:
        stop_watcher(_observer)
        _observer = None


def observe():
    global _observer
    if _observer:
        return

    def reload():
        note_db = DATABASE.resolve('dev_note')
        for note in note_db.query.all():
            port = 6000 + note.uid
            execute(
                ["bash", "-c", f"lsof -ti :{port} | xargs --no-run-if-empty kill -1"],
                privileged=True
            )

    handler = Handler(reload)
    _observer = start_watcher(handler)


def sync():
    env = DATABASE.resolve('env')
    token = env.query.filter_by(key='GIT_AUTH_TOKEN').first()
    token = token.value if token and token.production else None
    if not token:
        raise RuntimeError("GIT_AUTH_TOKEN not in env")

    repo = Repo(SANDBOX_DIR)
    if repo.is_dirty(untracked_files=True):
        repo.git.add(all=True)
        repo.index.commit("Auto-sync from sandbox")

    origin = repo.remotes.origin
    url = origin.config_reader.get("url")
    token_url = url.replace("https://", f"https://oauth2:{token}@")

    try:
        origin.set_url(token_url)
        origin.push(refspec="sandbox:sandbox")
    except GitCommandError as e:
        raise RuntimeError(f"Push failed: {e.stderr.strip()}")
    finally:
        origin.set_url(url)
