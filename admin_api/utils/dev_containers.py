from . import execute
from ..data import DATABASE
from root_dir import ROOT_PATH
from shared.debugger import log
from git import Repo
import docker, docker.errors

client = docker.from_env()

DOCKER_PATH = ROOT_PATH / "docker"
CACHE_DIR = DOCKER_PATH / "container_cache"
SANDBOX_DIR = DOCKER_PATH / "sandbox"
IMAGE_NAME = "sandbox"
REPO_URL = "https://github.com/GrowVolution/growvolution.org"
BRANCH = "sandbox"


def _get_container(name: str):
    try:
        return client.containers.get(name)
    except docker.errors.NotFound:
        return None


def _create_image():
    try:
        client.images.get(IMAGE_NAME)
        log("info", f"Image '{IMAGE_NAME}' exists.")
    except docker.errors.ImageNotFound:
        log("info", f"Building Docker image '{IMAGE_NAME}'...")
        client.images.build(path=str(DOCKER_PATH), tag=IMAGE_NAME)
        log("info", "Image built successfully.")


def _init_container(name: str):
    container = _get_container(name)
    if not container:
        log("warn", f"Container '{name}' not found.")
        return

    admins = DATABASE.resolve('admin')
    user = admins.query.filter_by(name=name).first()
    pubkey = user.container_key
    if not pubkey:
        log("warn", f"Container key for '{name}' not found.")
        return

    try:
        set_privs_result = container.exec_run(
            cmd=["chown", "-R", "1000:1000", "/home/admin"],
            user="root"
        )
        set_auth_result = container.exec_run(
            cmd=[
                "bash", "-c",
                f"echo '{pubkey.strip()}' >> /home/admin/.ssh/authorized_keys"
            ],
            user="admin"
        )
        if set_privs_result.exit_code == 0 and set_auth_result.exit_code == 0:
            log("info", f"Privileges updates and public key for '{name}' added to authorized_keys.")
        else:
            log("warn", f"Operation failed for '{name}': \n\n"
                        f"--- Privilege Update ---\n\n{set_privs_result.output.decode()}\n\n"
                        f"--- Set Authorization ---\n\n{set_auth_result.output.decode()}")
    except docker.errors.APIError as e:
        log("error", f"Docker exec failed for container '{name}': {str(e)}")


def start_container(name: str):
    _create_image()

    if _get_container(name):
        log("warn", f"Container '{name}' already running.")
        return

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not SANDBOX_DIR.exists():
        log("info", f"Cloning branch '{BRANCH}' from GitHub...")
        Repo.clone_from(REPO_URL, SANDBOX_DIR, branch=BRANCH)
        execute(['chown', '-R', 'admin:sudo', SANDBOX_DIR],
                privileged=True)

    log("info", f"Starting container '{name}'...")
    client.containers.run(
        IMAGE_NAME,
        name=name,
        detach=True,
        ports={"22/tcp": 2222},
        volumes={
            str(CACHE_DIR): {"bind": "/home/admin/.cache", "mode": "rw"},
            str(SANDBOX_DIR): {"bind": "/home/admin/growvolution.org", "mode": "rw"},

        }
    )
    log("info", f"Container '{name}' started.")
    _init_container(name)


def stop_container(name: str):
    container = _get_container(name)
    if container is None:
        log("warn", f"Container '{name}' not running.")
        return

    log("info", f"Stopping container '{name}'...")
    container.stop()

    log("info", "Committing container changes to image...")
    container.commit(repository=IMAGE_NAME)
    log("info", "Changes committed.")

    container.remove()
    log("info", f"Container '{name}' removed.")
