from django.db import models

# Create your models here.


class WorkInfo(models.Model):
    work_name = models.CharField(max_length=50, verbose_name='作业名称')
    platform = models.CharField(max_length=20, verbose_name='平台')
    province = models.CharField(max_length=30, verbose_name='省市')
    project = models.CharField(max_length=200, verbose_name='项目')
    work_info = models.TextField(verbose_name='作业描述')
    runway = models.IntegerField(verbose_name='执行方式')
    time_rule = models.CharField(max_length=100, blank=True, verbose_name='定时规则', null=True)
    start_time = models.IntegerField(verbose_name='开始时间', blank=True, null=True)
    end_time = models.IntegerField(verbose_name='结束时间', blank=True, null=True)
    run_user = models.CharField(max_length=50, verbose_name='创建人')
    work_status = models.IntegerField(verbose_name='作业状态')
    file_package_names = models.CharField(max_length=500, verbose_name='文件压缩包名称')
    run_status = models.IntegerField(verbose_name='执行进度', blank=True, null=True)
    host_list = models.TextField(verbose_name='主机列表')
    value_list = models.TextField(verbose_name='参数列表', blank=True, null=True)
    create_time = models.IntegerField(verbose_name='创建时间')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        verbose_name = '作业'
        verbose_name_plural = '作业信息'


class WorkLog(models.Model):
    work_id = models.CharField(max_length=10, verbose_name='作业ID')
    work_name = models.CharField(max_length=100, verbose_name='作业名称')
    log = models.TextField(verbose_name='日志')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)