from .. import UTILS
from root_dir import ROOT_PATH
from shared.debugger import log

import docker, docker.errors

CLIENT = docker.from_env()

DOCKER_PATH = ROOT_PATH / "docker"
CACHE_DIR = DOCKER_PATH / "container_cache"
SANDBOX_DIR = DOCKER_PATH / "sandbox"
IMAGE_NAME = "sandbox"

PROJECT_PATH_STR = "/home/admin/growvolution.org"


@UTILS.register('create_sandbox_image')
def create_image():
    try:
        CLIENT.images.get(IMAGE_NAME)
        log("info", f"Image '{IMAGE_NAME}' exists.")
    except docker.errors.ImageNotFound:
        log("info", f"Building Docker image '{IMAGE_NAME}'...")
        CLIENT.images.build(path=str(DOCKER_PATH), tag=IMAGE_NAME)
        log("info", "Image built successfully.")


@UTILS.register('docker_container')
def get_container(name: str):
    try:
        return CLIENT.containers.get(name)
    except docker.errors.NotFound:
        return None


@UTILS.register('container_exec')
def container_exec(name: str, command: list[str], user: str = "root"):
    container = get_container(name)
    if not container:
        log("warn", f"Container '{name}' not found.")
        return

    try:
        result = container.exec_run(command, user=user)
        if result.exit_code == 0:
            log("info", f"Successfully executed {command} for container '{name}'.")
        else:
            log("warn", f"Executing {command} failed for container '{name}':\n{result.output.decode()}")
    except docker.errors.APIError as e:
        log("error", f"Docker exec failed for container '{name}':\n{str(e)}")


@UTILS.register('stop_container')
def stop_container(name: str):
    container = get_container(name)
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
