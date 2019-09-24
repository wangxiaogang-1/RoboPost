from django.test import TestCase
from cryptography.fernet import Fernet
import json
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

try:
    scheduler.start()
except(KeyboardInterrupt, SystemExit):
    scheduler.shutdown()


def add_time(func, args, id, timi, start_date):
    # 循环执行，需要几个参数
    # 默认时间格式，days,hours,minutes,seconds
    add = scheduler.add_job(func, 'interval', start_date=start_date, hours=int(timi), args=(args,), id=str(id))
    return add


def add_one_time(func, args, id, timi):
    # 年月日，时分秒
    add = scheduler.add_job(func, 'date', args=(args,), run_date=timi, id=str(id))
    return add


def get_time(id):
    job = scheduler.get_job(job_id=str(id))

    return job


def rem_time(id):
    job = scheduler.remove_job(job_id=str(id))
    return job
