from apscheduler.schedulers.blocking import BlockingScheduler
from run import sendMail

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=8)
@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every one minute.')
    sendMail()