from django.contrib.auth.models import *
from django.db import models


# Create your models here.
class Module(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='模块名称')
    description = models.TextField(max_length=200, verbose_name='模块描述')
    url = models.TextField(max_length=200, verbose_name='模块链接',null=True)
    icon = models.CharField(max_length=50, verbose_name='模块图标',null=True)
    codename = models.CharField(max_length=50, verbose_name='模块代码', null=True)

class Function(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, related_name='module_function', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='功能名称')
    description = models.TextField(max_length=200, verbose_name='功能描述')
    url = models.TextField(max_length=200, verbose_name='功能链接', null=True)
    codename = models.CharField(max_length=50, verbose_name='功能代码', null=True)
