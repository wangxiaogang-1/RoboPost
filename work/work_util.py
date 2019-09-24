# coding:utf-8
from datetime import datetime, timedelta
from django.db.models import Count
import logging
from work import models
log = logging.getLogger('autoops')

# 按30天计算作业数据


def count_works_onemouth(request):
    log.info("按30天计算作业数据")
    now, yesterday, one, two, three, four, month = get_format_time()
    # 根据具体的时间和作业状态以柱状图的样式显示数据。-
    week5 = models.WorkInfo.objects.all().values('workstatus').annotate(count=Count('workstatus')). \
        values('workstatus', 'count').filter(starttime__lte=now).filter(starttime__gte=one)
    week4 = models.WorkInfo.objects.all().values('workstatus').annotate(count=Count('workstatus')). \
        values('workstatus', 'count').filter(starttime__lte=one).filter(starttime__gte=two)
    week3 = models.WorkInfo.objects.all().values('workstatus').annotate(count=Count('workstatus')). \
        values('workstatus', 'count').filter(starttime__lte=two).filter(starttime__gte=three)
    week2 = models.WorkInfo.objects.all().values('workstatus').annotate(count=Count('workstatus')). \
        values('workstatus', 'count').filter(starttime__lte=three).filter(starttime__gte=four)
    week = models.WorkInfo.objects.all().values('workstatus').annotate(count=Count('workstatus')). \
        values('workstatus', 'count').filter(starttime__lte=four).filter(starttime__gte=month)
    wait1, run1, success1, error1, stop1 = loop(week)
    wait2, run2, success2, error2, stop2 = loop(week2)
    wait3, run3, success3, error3, stop3 = loop(week3)
    wait4, run4, success4, error4, stop4 = loop(week4)
    wait5, run5, success5, error5, stop5 = loop(week5)

    list_wait = [wait1, wait2, wait3, wait4, wait5]
    list_run = [run1, run2, run3, run4, run5]
    list_success = [success1, success2, success3, success4, success5]
    list_error = [error1, error2, error3, error4, error5]
    list_stop = [stop1, stop2, stop3, stop4, stop5]
    month = {}
    month['wait'] = list_wait
    month['run'] = list_run
    month['success'] = list_success
    month['error'] = list_error
    month['stop'] = list_stop
    return month


# 自定义获取当前时间的方法
def get_format_time():
    tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # str
    now = datetime.strptime(str(tm), "%Y-%m-%d %H:%M:%S")  # datetime.datetime
    yesterday = now - timedelta(hours=24)
    one = now - timedelta(hours=24 * 6)
    two = now - timedelta(hours=24 * 12)
    three = now - timedelta(hours=24 * 18)
    four = now - timedelta(hours=24 * 24)
    month = now - timedelta(hours=24 * 30)
    # 转换为时间戳
    new_now = now.timestamp()
    new_yesterday = yesterday.timestamp()
    new_one = one.timestamp()
    new_two = two.timestamp()
    new_three = three.timestamp()
    new_four = four.timestamp()
    new_month = month.timestamp()
    # 因为数据库中存储的是Integer类型
    return int(new_now), int(new_yesterday), int(new_one), int(new_two), int(new_three), int(new_four), int(new_month)


def loop(week):
    list_week = list(week)
    wait, run, success, error, stop = '0', '0', '0', '0', '0'

    for i in list_week:
        if i['workstatus'] == '待确认':
            wait = (i['count'])
        if i['workstatus'] == '执行中':
            run = (i['count'])
        if i['workstatus'] == '执行成功':
            success = (i['count'])
        if i['workstatus'] == '执行错误':
            error = (i['count'])
        if i['workstatus'] == '执行中断':
            stop = (i['count'])
    return str(wait), str(run), str(success), str(error), str(stop)