from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

SCHEDULER = BackgroundScheduler()

SCHEDULER.add_job(
    func=update_cache,
    trigger=CronTrigger(hour=0, minute=0),
    id='sandbox_sync',
    replace_existing=True
)
