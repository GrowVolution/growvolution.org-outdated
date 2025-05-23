from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import os, subprocess, signal

load_dotenv()
env = os.environ.copy()
env['INSTANCE'] = 'debug'
env['SERVER_NAME'] = f"debug.{env['SERVER_NAME']}"

watch_dir = Path(__file__).parent / 'website'
logs_dir = Path(__file__).parent / 'logs' / 'debug'
process = None


def reload_dotenv():
    global env
    load_dotenv()
    env = os.environ.copy()
    env['INSTANCE'] = 'debug'
    env['SERVER_NAME'] = f"debug.{env['SERVER_NAME']}"


def clean_old_logs(log_dir: Path, max_files: int = 10, delete_count: int = 10):
    log_files = sorted(
        [f for f in log_dir.iterdir() if f.is_file()],
        key=lambda f: f.stat().st_mtime
    )

    if len(log_files) > max_files:
        to_delete = log_files[:delete_count]
        for f in to_delete:
            f.unlink() if f.exists() else None


class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if not event.src_path.endswith(('.py', '.html', '.css', '.js')):
            return
        if event.event_type not in ["modified", "deleted"]:
            return
        restart()


def start():
    global process

    clean_old_logs(logs_dir)
    clean_old_logs(logs_dir.parent)

    timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
    logs_dir.mkdir(parents=True, exist_ok=True)
    logfile = logs_dir / f"{timestamp}.log"
    process = subprocess.Popen(
        ['gunicorn', 'app:APP', '-b', '127.0.0.1:5001', '-k', 'eventlet'],
        env=env,
        stdout=open(logfile, 'w'),
        stderr=subprocess.STDOUT
    )


def restart():
    global process
    if process:
        process.send_signal(signal.SIGHUP)
    else:
        start()


def start_watcher() -> Observer:
    start()
    observer = Observer()
    observer.schedule(Handler(), str(watch_dir), recursive=True)
    observer.start()
    return observer


def stop_watcher(observer: Observer) -> None:
    observer.stop()
    process.terminate()
    observer.join()
    return None
