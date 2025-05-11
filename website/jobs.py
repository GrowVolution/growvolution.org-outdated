from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .cache import update_cache

SCHEDULER = BackgroundScheduler()

SCHEDULER.add_job(
    func=update_cache,
    trigger=CronTrigger(minute=0),
    id='cache_updater',
    replace_existing=True
)