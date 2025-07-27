from pathlib import Path
from datetime import datetime
import sys, subprocess, socket, os

ENV_GUNICORN = [sys.executable, '-m', 'gunicorn']
BASE_ENV = os.environ.copy()

_log_dir = Path(__file__).parent / 'logs' / 'admin_api'
_log_dir.mkdir(parents=True, exist_ok=True)

_host = '127.0.0.1'
_port = os.getenv('PORT', 5000)


def _port_in_use():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex((_host, _port))
        return result == 0


def timestamp():
    return datetime.now().strftime("%d%m%Y%H%M%S")


def start_api():
    logfile = _log_dir / f"{timestamp()}.log"
    return subprocess.Popen(
        ENV_GUNICORN + ['admin:app', '-b', f'{_host}:{_port}', '-k', 'eventlet'],
        stdout=open(logfile, 'w'),
        stderr=subprocess.STDOUT
    )


if not _port_in_use():
    proc = start_api()
    proc.wait()
