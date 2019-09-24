#coding=utf-8
from django import template
import datetime
import time

#创建模板库的实例
register = template.Library()

# 时间戳格式转换为日期字符串
@register.filter
def parse_timestamp(timestamp):
    if timestamp == None:
        return '-'
    time_obj = time.localtime(timestamp)
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
    return time_str

# 计算两个时间戳之间的时间差
@register.filter
def sub_timestamp(start_timestamp, end_timestamp):
    timestr = '-'
    print ()
    if start_timestamp != None and end_timestamp != None:
        start_time = datetime.datetime.utcfromtimestamp(start_timestamp)
        end_time = datetime.datetime.utcfromtimestamp(end_timestamp)
        sub_time = end_time - start_time
        # 相差天数
        sub_days = sub_time.days
        # 计算后剩余秒数
        sub_seconds = sub_time.seconds
        # 相差小时
        sub_hours = sub_seconds // (60*60)
        # 计算后剩余秒数
        sub_seconds = sub_seconds % (60*60)
        # 相差分钟数
        sub_minutes = sub_seconds // 60
        # 相差秒数
        sub_seconds = sub_seconds % 60
        timestr = sub_days.__str__() + '天 ' + sub_hours.__str__() + '小时 ' + sub_minutes.__str__() + '分钟 ' + sub_seconds.__str__() + '秒'
    return timestr

# 计算两个时间戳之间的时间差
@register.filter
def re_path(path):
    if '/' in path:
        paths = path.split('/')
    else:
        paths = path.split('\\')
    return paths[-1]

# 判断数据值是否相等
@register.filter
def compare_num(da1, da2):
    print (int(da1) == da2)
    return int(da1) == da2

# 备注版本
@register.filter
def translate_none(value):
    if value == None:
        value = '--'
    return value


