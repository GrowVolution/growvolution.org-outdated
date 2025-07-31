from . import UTILS
from .containers import SANDBOX_DIR
from .. import APP
from ..data import DATABASE
from shared.debugger import log

from git import Repo, GitCommandError
from datetime import datetime

REPO_URL = "https://github.com/GrowVolution/growvolution.org"
BRANCH = "sandbox"


@UTILS.register('fetch_sandbox')
def fetch_directory():
    if not SANDBOX_DIR.exists():
        log("info", f"Cloning branch '{BRANCH}' from GitHub...")
        Repo.clone_from(REPO_URL, SANDBOX_DIR, branch=BRANCH)


@UTILS.register('sync_sandbox')
def sync():
    env = DATABASE.resolve('env')
    with APP.app_context():
        token = env.query.filter_by(key='GIT_AUTH_TOKEN').first()
        token = token.value if token else None
        if not token:
            raise RuntimeError("GIT_AUTH_TOKEN not in env")

    repo = Repo(SANDBOX_DIR)
    if repo.is_dirty(untracked_files=True):
        repo.git.add(all=True)

        timestamp = datetime.now().strftime("%d/%m/%Y")
        repo.index.commit(f"{timestamp} - api auto-sync")

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
