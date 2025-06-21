from . import REDIS, APP
from .cache import update_cache
from .data.user import update_user_scores
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from debugger import log
import json, importlib

SCHEDULER = BackgroundScheduler()

SCHEDULER.add_job(
    func=update_cache,
    trigger=CronTrigger(minute=0),
    id='cache_updater',
    replace_existing=True
)

SCHEDULER.add_job(
    func=update_user_scores,
    trigger=CronTrigger(hour=23, minute=59),
    id='user_score_updater',
    replace_existing=True
)


def register_job(name: str):
    def decorator(func):
        module = func.__module__
        qualname = f"{module}.{func.__name__}"
        REDIS.hset('job_registry', name, qualname)
        return func
    return decorator


def queue_job(name: str, *args, **kwargs):
    job_data = {
        'func': name,
        'args': args,
        'kwargs': kwargs
    }
    REDIS.lpush('job_queue', json.dumps(job_data))


def _process_job(job_data: dict):
    path = REDIS.hget('job_registry', job_data['func'])
    if not path:
        log('error', "Could not load job data.")
        return

    path = path.decode()
    module_name, func_name = path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)

    try:
        func(APP, *job_data['args'], **job_data['kwargs'])
    except Exception as e:
        import sys, traceback
        tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
        log('error', f"Executing job {job_data['func']} failed:\n{type(e).__name__}: {e}\n{tb_str}")


def process_queue():
    while True:
        job = REDIS.rpop('job_queue')
        if job is None:
            break

        try:
            job_data = json.loads(job)
            log('info', f"Running job '{job_data['func']}'.")
            _process_job(job_data)
        except TypeError as e:
            log('error', f"Parsing or processing job failed: {e}")
