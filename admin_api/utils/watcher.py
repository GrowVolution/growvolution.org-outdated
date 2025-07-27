from .dev_containers import SANDBOX_DIR
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer

"""
env = os.environ.copy()
env['INSTANCE'] = 'debug'
env['SERVER_NAME'] = f"debug.{env['SERVER_NAME']}"
DEBUG_SUBROUTING = ''
env['DEBUG_SUBROUTING'] = DEBUG_SUBROUTING

def set_debug_routing(subsite: str):
    global DEBUG_SUBROUTING
    DEBUG_SUBROUTING = subsite
    env['DEBUG_SUBROUTING'] = subsite
"""


class Handler(FileSystemEventHandler):
    reload_blocked = False
    reload_scheduled = False

    def __init__(self, reload_fn: callable):
        super().__init__()
        self.reload_fn = reload_fn

    def reload(self):
        self.reload_fn()
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


def start_watcher(handler: Handler) -> Observer:
    observer = Observer()
    observer.schedule(handler, str(SANDBOX_DIR), recursive=True)
    observer.start()
    return observer


def stop_watcher(observer: Observer):
    observer.stop()
    observer.join()
