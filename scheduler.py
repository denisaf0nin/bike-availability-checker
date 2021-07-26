from apscheduler.schedulers.blocking import BlockingScheduler
from main import regular_check, scheduled_report

scheduler = BlockingScheduler()

regular_check = scheduler.add_job(regular_check, 'interval', minutes=15)
scheduled_report = scheduler.add_job(scheduled_report, 'cron', hour="12,15,18,22", timezone='Europe/Vilnius')

scheduler.start()
