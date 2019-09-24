# coding:utf-8
from django.contrib import admin
from . import models
from datetime import datetime
import time
# 方式一：
class MyConfig(admin.ModelAdmin):
    # 自定义显示字段
    list_display = ['work_name', 'work_type', 'build_time']

    def build_time(self):

        st = time.localtime(self.build_time)
        tt = time.strftime('%Y-%m-%d %H:%M:%S', st)
        return self.build_time



    # def __str__(self):
    #     st = time.localtime(self.build_time)
    #     tt = time.strftime('%Y-%m-%d %H:%M:%S', st)
    #     return tt



admin.site.register(models.Work, MyConfig)