from . import API
from ..data import DATABASE
from ..utils import get_latest_log
from ..utils.server_control import site_online, worker_running
import psutil

_not_running = ['--- not running ---']


@API.register('server_status')
def server_status(data):
    site_status = site_online()
    worker_status = worker_running()

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    api_log = []
    site_log = []
    worker_log = []

    if data.get('logs', False):
        api_log = get_latest_log('admin_api') or api_log
        site_log = get_latest_log() or site_log if site_status else _not_running
        worker_log = get_latest_log('worker') or worker_log if worker_status else _not_running


    admins = DATABASE.resolve('admin')
    usage = {
        'site_online': site_status,
        'worker_running': worker_status,

        'cpu_percent': round(cpu, 2),
        'memory_used': round(mem.used / (1024**3), 2),
        'memory_total': round(mem.total / (1024**3), 2),
        'memory_percent': round(mem.percent, 2),
        'disk_used': round(disk.used / (1024**3), 2),
        'disk_total': round(disk.total / (1024**3), 2),
        'disk_percent': round(disk.percent, 2),

        'api_log': api_log,
        'site_log': site_log,
        'worker_log': worker_log,

        'admins': admins.query.count()
    }

    return usage
