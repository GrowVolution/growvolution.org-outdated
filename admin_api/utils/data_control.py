from . import execute, load_env
from root_dir import ROOT_PATH
from shared.debugger import log
import sys

_initialized = {'api': False, 'site': False}
_cmd_template = [sys.executable, '-m', 'flask', 'db']
_api_addition = ['-d', 'migrations/admin']
_site_addition = ['-d', 'migrations/site']


def _exec(cmd, **kwargs):
    output, code = execute(
        cmd,
        return_as_result=True,
        privileged=True,
        **kwargs
    )

    output = output.decode() if isinstance(output, bytes) else output
    if code != 0:
        log("error", f"Error while executing command: {cmd}\n{output}")
        raise RuntimeError(output)

    return output


def _initialize(api: bool):
    flag = 'api' if api else 'site'

    global _initialized
    if _initialized[flag]:
        return

    migrations = ROOT_PATH / "migrations"
    migrations = migrations / "admin" if api else migrations / "site"
    if not migrations.exists():
        log("info", "Migration folder not found, initializing...")
        addition = _api_addition if api else _site_addition
        env = {'FLASK_APP': f"db_{'admin' if api else 'main'}.py", **({} if api else load_env())}
        output = _exec(
            [*_cmd_template, *addition, 'init'],
            env=env
        )
        log("info", f"Initialization finished:\n{output}")

    _initialized[flag] = True


def update_api_db(message: str = 'Auto update'):
    log("info", f"Running api database update '{message}'.")
    _initialize(True)

    env = {'FLASK_APP': 'db_admin.py'}
    output = _exec(
        [*_cmd_template, 'migrate', *_api_addition, '-m', message],
        env=env
    )
    log("info", f"Migration finished:\n{output}.")

    output = _exec(
        [*_cmd_template, 'upgrade', *_api_addition],
        env=env
    )
    log("info", f"Upgrade finished:\n{output}.")


def update_site_db(message: str = 'Auto update'):
    log("info", f"Running site database update '{message}'.")
    _initialize(False)

    env = {'FLASK_APP': 'db_main.py', **load_env()}
    output = _exec(
        [*_cmd_template, 'migrate', *_site_addition, '-m', message],
        env=env
    )
    log("info", f"Migration finished:\n{output}.")

    output = _exec(
        [*_cmd_template, 'upgrade', *_site_addition],
        env=env
    )
    log("info", f"Upgrade finished:\n{output}.")
