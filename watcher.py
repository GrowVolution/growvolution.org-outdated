from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from threading import Timer
import os, subprocess, signal

load_dotenv()
env = os.environ.copy()
env['INSTANCE'] = 'debug'
env['SERVER_NAME'] = f"debug.{env['SERVER_NAME']}"
DEBUG_SUBROUTING = ''
env['DEBUG_SUBROUTING'] = DEBUG_SUBROUTING

watch_dir = Path(__file__).parent / 'website'
logs_dir = Path(__file__).parent / 'logs' / 'debug'
process = None


def reload_dotenv():
    global env
    load_dotenv()
    env = os.environ.copy()
    env['INSTANCE'] = 'debug'
    env['SERVER_NAME'] = f"debug.{env['SERVER_NAME']}"
    env['DEBUG_SUBROUTING'] = DEBUG_SUBROUTING


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

    reload_blocked = False
    reload_scheduled = False

    def reload(self):
        restart()
        self.reload_blocked = True
        Timer(3, self.reload_timeout).start()

    def reload_timeout(self):
        if self.reload_scheduled:
            self.reload_scheduled = False
            self.reload()
            return
        self.reload_blocked = False

    def on_any_event(self, event):
        if not event.src_path.endswith(('.py', '.html', '.css', '.js')):
            return
        if event.event_type not in ["modified", "deleted", "moved"]:
            return

        if self.reload_blocked:
            self.reload_scheduled = True
            return

        self.reload()


def start():
    global process

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

    clean_old_logs(logs_dir)
    clean_old_logs(logs_dir.parent)


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


def set_debug_routing(subsite: str):
    global DEBUG_SUBROUTING
    DEBUG_SUBROUTING = subsite
    env['DEBUG_SUBROUTING'] = subsite
