from . import APP
from .utils import UTILS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

SCHEDULER = BackgroundScheduler()

if not APP.config['SANDBOX_MODE']:
    SCHEDULER.add_job(
        func=UTILS.resolve('sync_sandbox'),
        trigger=CronTrigger(hour=0, minute=0),
        id='sandbox_sync',
        replace_existing=True
    )
