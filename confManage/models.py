from django.db import models

# Create your models here.

# 本机包存放目录；目标机器包存放目录；目标机器备份目录


class PublicParameter(models.Model):
    confK = models.CharField(max_length=500, verbose_name='配置键')
    confV = models.CharField(max_length=500, verbose_name='配置值')
    confI = models.TextField(max_length=1000, verbose_name='配置信息', null=True)


class HostInfo(models.Model):
    IP = models.GenericIPAddressField(max_length=15, verbose_name='机器IP')
    host_name = models.CharField(max_length=100, verbose_name='主机名')
    # 应用服务器，数据库服务器
    server_type = models.CharField(max_length=50, verbose_name='服务器类别')
    platform = models.CharField(max_length=50, verbose_name='平台')
    province = models.CharField(max_length=50, verbose_name='省市')
    project = models.CharField(max_length=200, verbose_name='项目')
    account = models.CharField(max_length=50, verbose_name='账号')
    password = models.CharField(max_length=500, verbose_name='密码')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', null=True)


class DBInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name='数据库名')
    account = models.CharField(max_length=50, verbose_name='账号')
    password = models.CharField(max_length=500, verbose_name='密码')
    tnsname = models.CharField(max_length=500, verbose_name='连接数据库的别名参数')
    port = models.IntegerField(verbose_name='端口', null=True, blank=True)
    sid = models.CharField(max_length=200, verbose_name='SID')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', null=True)
    host_ip = models.ForeignKey(HostInfo, on_delete=models.CASCADE)


class ProjectInfo(models.Model):
    app_directory = models.CharField(max_length=200, verbose_name='应用目录')
    middleware_type = models.CharField(max_length=200, verbose_name='中间件类别')
    middleware_name = models.CharField(max_length=200, verbose_name='项目账号')
    middleware_pass = models.CharField(max_length=500, verbose_name='项目密码')
    url = models.CharField(max_length=200, verbose_name='url地址')
    restart_script_path = models.CharField(max_length=200, verbose_name='重启脚本路径')
    static_directory = models.CharField(max_length=200, verbose_name='静态目录')
    cache_directory = models.CharField(max_length=200, verbose_name='缓存目录')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', null=True)
    host_ip = models.ForeignKey(HostInfo, on_delete=models.CASCADE)