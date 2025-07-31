from . import UTILS
from .containers import SANDBOX_DIR
from .. import APP
from ..data import DATABASE
from shared.debugger import log
from root_dir import ROOT_PATH

from git import Repo, GitCommandError
from datetime import datetime

REPO_URL = "https://github.com/GrowVolution/growvolution.org"
BRANCH = "sandbox"


def _inject_token(origin):
    env = DATABASE.resolve('env')
    with APP.app_context():
        token = env.query.filter_by(key='GIT_AUTH_TOKEN').first()
        token = token.value if token else None
        if not token:
            raise RuntimeError("GIT_AUTH_TOKEN not in env")

    url = origin.config_reader.get("url")
    token_url = url.replace("https://", f"https://oauth2:{token}@")
    origin.set_url(token_url)
    return origin, url


def _perform_push(origin, branch):
    origin, url = _inject_token(origin)
    try:

        origin.push(refspec=f"{branch}:{branch}")
    except GitCommandError as e:
        raise RuntimeError(f"Push failed: {e.stderr.strip()}")
    finally:
        origin.set_url(url)


@UTILS.register('fetch_sandbox')
def fetch_directory():
    if not SANDBOX_DIR.exists():
        log("info", f"Cloning branch '{BRANCH}' from GitHub...")
        Repo.clone_from(REPO_URL, SANDBOX_DIR, branch=BRANCH)


@UTILS.register('sync_sandbox')
def sync(main: bool = False):
    repo = Repo(ROOT_PATH if main else SANDBOX_DIR)
    if repo.is_dirty(untracked_files=True):
        repo.git.add(all=True)

        timestamp = datetime.now().strftime("%d/%m/%Y")
        repo.index.commit(f"{timestamp} - api auto-sync")

    branch = "main" if main else BRANCH
    _perform_push(repo.remotes.origin, branch)


@UTILS.register('merge_branches')
def merge_branches():
    main_repo = Repo(ROOT_PATH)
    if main_repo.is_dirty(untracked_files=True):
        log('warn', "Uncommitted changes in 'main' - running auto-sync...")
        sync(True)

    origin_main = main_repo.remotes.origin
    origin_main.fetch()

    main_repo.git.checkout(BRANCH)
    main_repo.git.merge('main')
    _perform_push(origin_main, BRANCH)
    log("info", "Merged 'main' into 'sandbox' and pushed.")

    main_repo.git.checkout('main')

    sandbox_repo = Repo(SANDBOX_DIR)
    if sandbox_repo.is_dirty(untracked_files=True):
        log('warn', "Uncommitted changes in 'sandbox' - running auto-sync...")
        sync()

    origin_sandbox = sandbox_repo.remotes.origin
    origin_sandbox.fetch()

    sandbox_repo.git.checkout('main')
    sandbox_repo.git.merge('sandbox')
    _perform_push(origin_sandbox, 'main')
    log("info", "Merged 'sandbox' into 'main' and pushed.")

    sandbox_repo.git.checkout(BRANCH)
