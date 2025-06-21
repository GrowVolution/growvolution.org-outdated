from  website.jobs import process_queue
from apscheduler.schedulers.blocking import BlockingScheduler
from debugger import log

WORKER = BlockingScheduler()

WORKER.add_job(
    func=process_queue,
    trigger='interval',
    seconds=3
)


if __name__ == '__main__':
    log('info', "Worker thread started.")
    log('info', "Processing queue every 3 seconds.")
    WORKER.start()
