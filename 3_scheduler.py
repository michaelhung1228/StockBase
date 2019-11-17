import os, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from datetime import datetime
from datetime import timedelta
import sqlite3

delta_2min = timedelta(minutes = 2)

def build_stock_day_data():
    os.system("python 3_build_stock_day_data.py")

sched = BackgroundScheduler()
sched.add_job(build_stock_day_data, 'interval', minutes = 3, id = '001', next_run_time = datetime.now(), max_instances = 1)

sched.start()

while 1:
    print(sched.get_job('001'))

    time.sleep(60)