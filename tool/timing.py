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


def add_time(func, args, id, time):

    xx = time.split(',')

    add = scheduler.add_job(func, 'cron', args=(args),
                           second=xx[5], minute=xx[4],
                           hour=xx[3], day=xx[2], month=xx[1],
                           year=xx[0], id=str(id))
    return add


def get_time(id):

    job = scheduler.get_job(job_id=id)

    return job


def rem_time(id):
    job = scheduler.remove_job(job_id=id)
    return job


