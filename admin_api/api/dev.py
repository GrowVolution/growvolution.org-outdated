from . import API
from ..utils import UTILS
from shared.debugger import log

import sys


def _exec(*args):
    execute = UTILS.resolve('exec')
    load_env = UTILS.resolve('load_env')

    return execute(
        [sys.executable, 'dev_tokens.py', *args],
        env=load_env(),
        return_as_result=True
    )


@API.register('dev_tokens')
def manage_tokens(data):
    response = { 'success': False }
    cmd = data.get("cmd")

    match cmd:
        case '1':
            name = data.get("name")
            if not name:
                response['error'] = "Missing data"
                return response
            valid_opt = data.get("valid_opt")
            output, code = _exec('create_token', name, valid_opt)

        case '2':
            name = data.get("name")
            if not name:
                response['error'] = "Missing data"
                return response
            output, code = _exec('delete_token', name)

        case '3':
            output, code = _exec('list_tokens')

        case _:
            response['error'] = f"Invalid command ({cmd})"
            return response

    if code != 0:
        response['error'] = f"Process exited with code: {code}"
        log('error', f"Error occurred while dev_token action: {cmd}\n"
                     f"{output}")
        return response

    response['success'] = True
    response['output'] = output.split('\n')
    return response
