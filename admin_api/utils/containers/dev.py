from . import CLIENT, IMAGE_NAME, CACHE_DIR, SANDBOX_DIR, PROJECT_PATH_STR
from .. import UTILS
from ...data import DATABASE
from shared.debugger import log


def _init_container(name: str):
    admins = DATABASE.resolve('admin')
    user = admins.query.filter_by(name=name).first()
    pubkey = user.container_key
    if not pubkey:
        log("warn", f"Container key for '{name}' not found.")
        return

    container_exec = UTILS.resolve('container_exec')
    container_exec(name, ["bash", "-c", "chown -R admin:sudo /home/admin"])
    container_exec(name, [
            "bash", "-c",
            f"echo '{pubkey.strip()}' >> /home/admin/.ssh/authorized_keys"
        ], "admin"
    )


@UTILS.register('start_dev_container')
def start_container(name: str):
    get_container = UTILS.resolve('docker_container')
    if get_container(name):
        log("warn", f"Container '{name}' already running.")
        return

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    log("info", f"Starting container '{name}'...")
    CLIENT.containers.run(
        IMAGE_NAME,
        name=name,
        detach=True,
        ports={"22/tcp": 2222},
        volumes={
            str(CACHE_DIR): {"bind": "/home/admin/.cache", "mode": "rw"},
            str(SANDBOX_DIR): {"bind": PROJECT_PATH_STR, "mode": "rw"}
        },
        entrypoint=["/usr/sbin/sshd", "-D"]
    )
    log("info", f"Container '{name}' started.")
    _init_container(name)
