from django.db import models

# Create your models here.
class Script(models.Model):
    functionName = models.CharField(max_length=100, verbose_name='功能名称')
    scriptInfo = models.TextField(verbose_name='脚本内容')
    scriptCode = models.CharField(max_length=100, verbose_name='脚本编码')
    scriptType = models.CharField(max_length=20, verbose_name='脚本类型')
    scriptLanguage = models.CharField(max_length=20, verbose_name='脚本语言')
    paramList = models.TextField(verbose_name='参数列表')
    author = models.CharField(max_length=20, verbose_name='脚本作者')
    uploadTime = models.IntegerField(verbose_name='脚本上传时间')
    filename = models.CharField(max_length=100, verbose_name='文件名称')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', null=True)


class Templet(models.Model):
    temName = models.CharField(max_length=100, verbose_name='模板名称')
    orderList = models.CharField(max_length=100, verbose_name='顺序列表')
    templet_type = models.CharField(max_length=100, verbose_name='模板类别')
    temIntroduce = models.TextField(verbose_name='模板介绍')
    author = models.CharField(max_length=10, verbose_name='模板作者')
    createTime = models.IntegerField(verbose_name='模板创建时间')
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', null=True)