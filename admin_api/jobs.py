from .utils.sandbox_control import sync as sandbox_sync
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

SCHEDULER = BackgroundScheduler()

SCHEDULER.add_job(
    func=sandbox_sync,
    trigger=CronTrigger(hour=0, minute=0),
    id='sandbox_sync',
    replace_existing=True
)
