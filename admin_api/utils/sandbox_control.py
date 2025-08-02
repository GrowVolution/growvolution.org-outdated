from . import UTILS
from .containers import SANDBOX_DIR, DOCKER_PATH
from .. import APP
from ..data import DATABASE
from shared.debugger import log
from root_dir import ROOT_PATH

from datetime import datetime

REPO_URL = "https://github.com/GrowVolution/growvolution.org"
BRANCH = "sandbox"


def _get_token_url():
    env = DATABASE.resolve('env')
    with APP.app_context():
        token = env.query.filter_by(key='GIT_AUTH_TOKEN').first()
        token = token.value if token else None
        if not token:
            raise RuntimeError("GIT_AUTH_TOKEN not in env")
    return REPO_URL.replace("https://", f"https://oauth2:{token}@")


def _git(args, cwd):
    execute = UTILS.resolve('exec')
    output, code = execute(
        ["git"] + args,
        cwd=str(cwd),
        return_as_result=True
    )
    if code != 0:
        raise RuntimeError(f"Git error: {output}")
    return output


def _commit_if_dirty(cwd):
    status = _git(["status", "--porcelain"], cwd)
    if status:
        _git(["add", "-A"], cwd)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        _git(["commit", "-m", f"{timestamp} - api auto-sync"], cwd)


@UTILS.register('fetch_sandbox')
def fetch_directory():
    if not SANDBOX_DIR.exists():
        log("info", f"Cloning branch '{BRANCH}' from GitHub...")
        repo_url = _get_token_url()
        _git(["clone", "-b", BRANCH, repo_url, str(SANDBOX_DIR)], cwd=DOCKER_PATH)


@UTILS.register('sync_sandbox')
def sync(main: bool = False):
    cwd = ROOT_PATH if main else SANDBOX_DIR
    branch = "main" if main else BRANCH

    try:
        _git(["checkout", branch], cwd)
    except RuntimeError:
        log("error", f"Branch '{branch}' not found.")
        return

    try:
        _git(["pull", _get_token_url(), branch], cwd)
    except RuntimeError as e:
        log("warn", str(e))

    try:
        _commit_if_dirty(cwd)
    except RuntimeError as e:
        log("warn", str(e))

    try:
        _git(["push", _get_token_url(), branch], cwd)
    except RuntimeError as e:
        log("error", str(e))


@UTILS.register('merge_branches')
def merge_branches():
    sync(True)
    main_repo = ROOT_PATH

    try:
        _git(["checkout", BRANCH], main_repo)
        _git(["merge", "main"], main_repo)
        _git(["push", _get_token_url(), BRANCH], main_repo)
        log("info", "Merged 'main' into 'sandbox' and pushed.")

        _git(["checkout", "main"], main_repo)
    except RuntimeError as e:
        log("error", str(e))

    sync()
    sandbox_repo = SANDBOX_DIR

    try:
        _git(["checkout", "main"], sandbox_repo)
        _git(["merge", BRANCH, "-X", "theirs"], sandbox_repo)
        _git(["push", _get_token_url(), "main"], sandbox_repo)
        log("info", "Merged 'sandbox' into 'main' and pushed.")

        _git(["checkout", BRANCH], sandbox_repo)
    except RuntimeError as e:
        log("error", str(e))
