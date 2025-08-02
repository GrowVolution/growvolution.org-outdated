from admin_api.api import API
from admin_api.utils import UTILS

from pathlib import Path


def _clean_path(path):
    return "/home/admin" if path == '~' else path


@API.register('bash')
def bash(data):
    response = { 'success': False }

    cmd = data.get('cmd')
    if not (cmd and isinstance(cmd, list)):
        response['error'] = "Invalid data"
        return response

    path = _clean_path(data.get('path', '~'))
    privileged = False
    if cmd[0] == "sudo":
        privileged = True
        cmd.pop(0)

    execute = UTILS.resolve('exec')
    output, _ = execute(
        cmd,
        cwd=path,
        privileged=privileged,
        return_as_result=True
    )

    response['output'] = output
    response['success'] = True
    return response


@API.register('check_path')
def path_exists(data):
    path = _clean_path(data.get('path', '~'))
    return { 'exists': Path(path).exists() }
