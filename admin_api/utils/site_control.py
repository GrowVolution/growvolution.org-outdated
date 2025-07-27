from . import LOG_DIR, execute, load_env
from main import ENV_GUNICORN, timestamp
import subprocess, signal, sys, os

_main_proc = None
_worker_proc = None
_port = os.getenv("PORT")
_port = _port + 1000 if _port else 5001

def start_main():
    global _main_proc
    if _main_proc:
        stop_main()

    logfile = LOG_DIR / f"{timestamp()}.log"
    _main_proc = execute(
        ENV_GUNICORN + ['app:app', '-b', f'127.0.0.1:{_port}', '-k', 'eventlet'],
        env=load_env(),
        stdout=open(logfile, 'w'),
        stderr=subprocess.STDOUT
    )


def stop_main():
    global _main_proc
    if _main_proc:
        _main_proc.terminate()
        _main_proc = None


def restart_main(reload: bool = False):
    if _main_proc and reload:
        _main_proc.send_signal(signal.SIGHUP)
        return

    stop_main()
    start_main()


def start_worker():
    global _worker_proc
    worker_logs = LOG_DIR / "worker"
    worker_logs.mkdir(parents=True, exist_ok=True)
    log_file = worker_logs / f"{timestamp()}.log"
    _worker_proc = execute(
        [sys.executable, 'worker.py'],
        env=load_env(),
        stdout=open(log_file, 'w'),
        stderr=subprocess.STDOUT
    )


def stop_worker():
    global _worker_proc
    if _worker_proc:
        _worker_proc.terminate()
        _worker_proc = None


def restart_worker():
    stop_worker()
    start_worker()


def site_online() -> bool:
    return _main_proc is not None and _main_proc.poll() is None


def worker_running() -> bool:
    return _worker_proc is not None and _worker_proc.poll() is None
