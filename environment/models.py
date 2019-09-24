from django.db import models

# Create your models here.


class Template(models.Model):
    temp_name = models.CharField(verbose_name='模板名称', max_length=100)
    temp_type = models.CharField(verbose_name='模板类型', max_length=100, default='测试')
    belong_sys = models.CharField(verbose_name='所属系统', max_length=100)
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        # 定义model在数据库中的表名称
        db_table = "template"

    def __str__(self):
        return self.temp_name


class Application(models.Model):
    app_ip = models.CharField(verbose_name='应用机器ip', max_length=20)
    hostname = models.CharField(verbose_name='主机名', max_length=100)
    account = models.CharField(verbose_name='机器账号', max_length=100)
    password = models.CharField(verbose_name='机器密码', max_length=100)
    app_directory = models.CharField(verbose_name='应用目录', max_length=500)
    middleware_name = models.CharField(verbose_name='中间件账号', max_length=100)
    middleware_pass = models.CharField(verbose_name='中间件密码', max_length=100)
    url = models.CharField(verbose_name='url路径', max_length=500)
    upload_path = models.CharField(verbose_name='jar包上传路径', max_length=500)
    port = models.CharField(verbose_name='进程端口号', max_length=10)
    log_path = models.CharField(verbose_name='日志目录路径', max_length=500)
    env_type = models.CharField(verbose_name='所属环境类型', max_length=100)
    temp_id = models.ForeignKey(Template, verbose_name='模板外键', on_delete=models.CASCADE)
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        # 定义model在数据库中的表名称
        db_table = "application"


class Database(models.Model):
    db_ip = models.CharField(verbose_name='数据库机器ip', max_length=20)
    hostname = models.CharField(verbose_name='主机名', max_length=100)
    account = models.CharField(verbose_name='机器账号', max_length=100)
    password = models.CharField(verbose_name='机器密码', max_length=100)
    db_name = models.CharField(verbose_name='数据库名称', max_length=100)
    db_account = models.CharField(verbose_name='数据库账号', max_length=100)
    db_password = models.CharField(verbose_name='数据库密码', max_length=100)
    port = models.CharField(verbose_name='数据库端口', max_length=10)
    env_type = models.CharField(verbose_name='所属环境类型', max_length=100)
    temp_id = models.ForeignKey(Template, verbose_name='模板外键', on_delete=models.CASCADE)
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        # 定义model在数据库中的表名称
        db_table = "database"


class Config(models.Model):
    conf_key = models.CharField(verbose_name='配置健', max_length=500)
    conf_value = models.CharField(verbose_name='配置值', max_length=500)
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        # 定义model在数据库中的表名称
        db_table = "config"


class Work(models.Model):
    work_name = models.CharField(verbose_name='作业名称', max_length=100)
    work_type = models.CharField(verbose_name='作业类型', max_length=100, blank=True, null=True)
    work_status = models.CharField(verbose_name='作业状态', max_length=100)
    belong_sys = models.CharField(verbose_name='所属系统', max_length=100, blank=True, null=True)
    run_way = models.CharField(verbose_name='执行方式', max_length=10, default='手动')
    start_time = models.IntegerField(verbose_name='任务开始时间', blank=True, null=True)
    end_time = models.IntegerField(verbose_name='任务结束时间', blank=True, null=True)
    total_time = models.IntegerField(verbose_name='总耗时', blank=True, null=True)
    zip_name = models.TextField(verbose_name='压缩包名', blank=True, null=True)
    build_time = models.IntegerField(verbose_name='作业创建时间', blank=True, null=True)
    version = models.CharField(verbose_name='版本号', max_length=50, blank=True, null=True)
    value_list = models.TextField(verbose_name='参数列表', default='')
    temp_id = models.CharField(verbose_name='模板id', max_length=10)
    webapps_name = models.CharField(verbose_name='备份文件名', max_length=1000, blank=True, null=True)
    jar_name = models.CharField(verbose_name='jar包名称', max_length=1000, blank=True, null=True)
    time_rule = models.CharField(verbose_name='定时规则', max_length=100, blank=True, null=True)
    publish_way = models.CharField(verbose_name='发布方式', max_length=100, blank=True, null=True)
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        # 定义model在数据库中的表名称
        db_table = "work"

    # def __str__(self):
    #     return self.work_name


class Log(models.Model):
    log_name = models.CharField(verbose_name='日志名称', max_length=100)
    log_info = models.TextField(verbose_name='日志内容', blank=True, null=True)
    work_id = models.ForeignKey(Work, verbose_name='作业外键', default=1, on_delete=models.CASCADE)
    extend1 = models.CharField(max_length=1000, verbose_name='扩展字段1', blank=True, null=True)
    extend2 = models.CharField(max_length=1000, verbose_name='扩展字段2', blank=True, null=True)
    extend3 = models.CharField(max_length=1000, verbose_name='扩展字段3', blank=True, null=True)

    class Meta:
        # 定义model在数据库中的表名称
        db_table = "log"
