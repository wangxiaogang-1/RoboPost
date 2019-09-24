# 获取模板的配置阶段
import os
import socket
import time
import django
import pypinyin
from django.db.models import Q
from environment.loop_time import *
from django.db.models import Count
from pypinyin.constants import Style
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RoboPost.settings")
django.setup()
import logging
from datetime import datetime, timedelta
from environment.models import *
from django.contrib.auth.models import Group, User
logging = logging.getLogger('autoops')


def get_user_group(user):
    if not user.is_superuser:
        try:
            system = list(Group.objects.filter(user=user).values())[0]
            return system['name']
        except Exception as e:
            return '无权限'
    else:
        system = list(Group.objects.filter(user=user).values())[0]
        return system['name']


# 配置机器后返回模板配置阶段
def get_config_step(temp):
    lista = []
    config_step = []
    for i in list(Application.objects.filter(temp_id=temp)):
        config_step.append(i.env_type)
    lista.append(set(config_step).__len__())


def chose_temp_by_custom(user):
    system = get_user_group(user)
    temps = Template.objects.filter(Q(belong_sys=system) & Q(extend1=1))
    return temps


# 根据权限获取模板
def get_template(user):
    # 普通用户
    if not user.is_superuser:
        system = get_user_group(user)
        # 公共模板
        pub_temps = Template.objects.filter(Q(belong_sys=system) & Q(extend1=1)).all()
        # 私有模板
        pri_temps = Template.objects.filter(belong_sys=system).exclude(extend1=1).all()

    else:
        pub_temps = Template.objects.filter(extend1=1).all()
        pri_temps = Template.objects.exclude(extend1=1).all()

    return pub_temps, pri_temps


def get_template2(user):
    if not user.is_superuser:
        system = get_user_group(user)

        temps = Template.objects.filter(belong_sys=system).all()
    else:
        temps = Template.objects.all()
    return temps


# 根据模板获取应用服务器和数据库服务器
def get_all_server(temp, wtype):
    print(wtype)
    apps = Application.objects.filter(temp_id=temp).filter(env_type=wtype)
    # 目前对方是没有db环境的所以不需要考虑
    # dbs = Database.objects.filter(temp_id=temp)

    return apps


def get_one_server(id):
    app = Application.objects.get(id=id)
    return app


# 根据id获取模板的类型
def get_temp_type(id):
    type = Template.objects.filter(id=id).values('temp_type')
    return list(type)[0]['temp_type']


# 获取所有作业
def get_works(temp_name):
    works = Work.objects.filter(temp_name=temp_name).all()


# 根据所属环境查询db和app
def get_server_by_env(temp):
    apps = Application.objects.filter(temp_id=temp)
    dbs = Database.objects.filter(temp_id=temp)
    return apps, dbs


# 根据模板id获取模板
def get_temp_by_id(id):
    temp = Template.objects.filter(id=id)
    app = Application.objects.filter(temp_id=temp)
    # db = Database.objects.filter(temp_id=temp)
    return {
        'temp': temp,
        'app': app
    }


# get_tempappserver
def get_tempappserver(id):
    data = list(Application.objects.filter(temp_id=Template.objects.filter(id=id)).values('id', 'app_ip'))
    return data


# 根据ID获取模板和APP
def get_tAa(request):
    temp = Template.objects.get(id=request.GET.get('temp_id'))
    app = Application.objects.get(id=request.GET.get('app_id'))
    return {
        'temp': temp,
        'host': app
    }


def create_temp(temp):
    try:
        temp = Template.objects.update_or_create(**temp)
        return temp[0]
    except Exception as e:
        raise e


def update_temp(temp):
    try:
        Template.objects.filter(id=temp['id']).update(**temp)
    except Exception as e:
        raise e


def delete_temp(temp_id):
    r = 'failed'
    delete_tmp = Template.objects.filter(id=temp_id).delete()
    if delete_tmp[0] != 0:
        r = 'success'
    return r


def get_temps_count(temp_name):
    count = Template.objects.filter(temp_name=temp_name).count()
    return count

def create_application(application):
    try:
        application = Application.objects.create(**application)
        return application
    except Exception as e:
        raise e


def update_application(application):
    try:
        Application.objects.filter(id=application['id']).update(**application)
    except Exception as e:
        raise e


def delete_application(app_id):
    r = 'failed'
    delete_app = Application.objects.filter(id=app_id).delete()
    if delete_app[0] != 0:
        r = 'success'
    return r


def create_database(database):
    try:
        Database.objects.create(**database)
    except Exception as e:
        raise e


def update_database(database):
    try:
        Database.objects.filter(id=database['id']).update(**database)
    except Exception as e:
        raise e


def delete_database(database):
    delete_db = Database.objects.filter(id=database['id']).delete()
    if delete_db[0] != 0:
        print('删除成功')


def update_work(work):
    try:
        Work.objects.filter(id=work['id']).update(**work)
    except Exception as e:
        raise e


def delete_work(work_id):
    result = 'failed'
    work = Work.objects.get(id=work_id)
    if work.run_way == '定时':
        rem_time(work_id)
    delete_work = work.delete()
    if delete_work[0] != 0:
        result = 'success'
    return result

# 仪表盘相关的查询内容
# 获取系统所有组信息
def get_groups_name():
    names = list(Group.objects.all().values('name'))
    group_list = []
    for i in names:
        group_list.append(i['name'])
    return group_list


# 获取对应系统下的所有服务器
def get_all_server_account(user):
    if user.is_superuser:
        # 获取所有权限下的模板
        group_list = get_groups_name()

        da_list = []

        for i in group_list:
            count_dict = {}
            temps = Template.objects.filter(belong_sys=i)
            app_count = 0
            db_count = 0
            for temp in temps:
                app_count += Application.objects.filter(temp_id=temp).count()
                db_count += Database.objects.filter(temp_id=temp).count()
            count_dict['id'] = h2p(i)
            count_dict['count'] = str(app_count) + ',' + str(db_count)
            count_dict['desc'] = i
            da_list.append(count_dict)
        return da_list

    else:
        temps = get_template2(user)
        group = get_user_group(user)
        app_count = 0
        db_count = 0
        da_list = []
        da_dict = {}
        for temp in temps:
            app_count += Application.objects.filter(temp_id=temp).count()
            db_count += Database.objects.filter(temp_id=temp).count()
        da_dict['id'] = h2p(group)
        da_dict['count'] = str(app_count) + ',' + str(db_count)
        da_dict['desc'] = group

        da_list.append(da_dict)
        return da_list


# 通过组名获取用户数量
def get_user_amount(user):
    if user.is_superuser:
        group_list = get_groups_name()
        da_list = []

        for i in group_list:
            count_dict = {}
            users = User.objects.filter(groups__name=i).count()
            count_dict['id'] = h2p(i)
            count_dict['count'] = users
            count_dict['desc'] = i
            da_list.append(count_dict)
        return da_list
    else:
        da_list = []
        da_dict = {}
        group_name = get_user_group(user)
        users = User.objects.filter(groups__name=group_name).count()
        da_dict['id'] = h2p(group_name)
        da_dict['count'] = users
        da_dict['desc'] = group_name
        da_list.append(da_dict)
        return da_list


def h2p(hanzi):
    """
    :param hanzi: 传入汉字
    :return: 转出拼音
    """
    # pinyin = pypinyin.slug(hanzi, separator='', style=Style.FIRST_LETTER)
    # 下面是全称拼音用法
    pinyin = pypinyin.slug(hanzi, separator='')
    return pinyin


def success_failure_month(user):
    if user.is_superuser:
        group_list = get_groups_name()
        count_dict = {}
        for i in group_list:
            users = User.objects.filter(groups__name=i).count()
            count_dict[h2p(i)] = users
        return count_dict
    else:
        group_name = get_user_group(user)
        users = User.objects.filter(groups__name=group_name).count()
        return users


def get_30day(number=30):
    if int(number) < 2:
        number = 2
    tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # str
    now = datetime.strptime(str(tm), "%Y-%m-%d %H:%M:%S")  # datetime.datetime

    # 循环
    list_one = []
    count = 1
    list_one.append(int(now.timestamp()))
    while count <= number - 1:
        day = now - timedelta(days=count)
        list_one.append(int(day.timestamp()))
        count += 1
    list_one.reverse()
    return list_one
#总览页通过前后时间戳传值


def show_start_end(start, end):
    # 开始时间
    # 结束时间
    # 代表间隔天数
    time_list = []
    total = (int(end) - int(start))//86400
    if total == 0:
        total =2
    for i in range(total):
        time_list.append(end)
        end -= 86400
        if end == start:
            time_list.append(end)
            break
    time_list.reverse()
    return time_list


def translate(list_one, user):
    if user.is_superuser:
        data = {}
        data['month'] = {}
        data['month']['data_success'], data['month']['data_error'], data['month']['timestamp_month'] = [], [], []
        groups = get_groups_name()
        for i in list_one:
            success = Work.objects.filter(work_status='执行成功').filter(
                Q(start_time__lte=i) & Q(start_time__gte=i - 86400)).count()
            # '执行中断'，'执行失败',''
            error = Work.objects.filter(work_status__in=('执行中断', '执行异常')).filter(Q(start_time__lte=i) & Q(
                start_time__gte=i - 86400)).count()
            data['month']['data_success'].append(success)
            data['month']['data_error'].append(error)
        data['month']['timestamp_month'] = list_one

        list_da = []
        for group in groups:
            da = {}
            works = Work.objects.filter(belong_sys=group).filter(
                Q(start_time__lte=list_one[-1]) & Q(start_time__gte=list_one[0])).count()
            da['id'] = h2p(group)
            da['count'] = works
            da['desc'] = group
            list_da.append(da)
        data['sys_count'] = list_da
        work_status = list(Work.objects.
                           filter(Q(start_time__lte=list_one[-1])
                                  & Q(start_time__gte=list_one[0])).extra({'name': 'work_status'}).
                           values('name').annotate(value=Count('work_status')))
        data['work_status'] = work_status
    else:
        group_name = get_user_group(user)
        data = {}
        data['month'] = {}
        data['month']['data_success'], data['month']['data_error'], data['month']['timestamp_month'] = [], [], []
        for i in list_one:
            success = Work.objects.filter(Q(work_status='执行成功') & Q(belong_sys=group_name)).filter(
                Q(start_time__lte=i) & Q(start_time__gte=i - 86400)).count()
            # '执行中断'，'执行失败',''
            error = Work.objects.filter(work_status__in=('执行中断', '执行异常')).filter(Q(start_time__lte=i) & Q(
                start_time__gte=i - 86400)).filter(belong_sys=group_name).count()
            data['month']['data_success'].append(success)
            data['month']['data_error'].append(error)
        my_work = Work.objects.filter(belong_sys=group_name).filter(
            Q(start_time__lte=list_one[-1]) & Q(start_time__gte=list_one[0])).count()
        other_work = Work.objects.exclude(belong_sys=group_name).filter(
            Q(start_time__lte=list_one[-1]) & Q(start_time__gte=list_one[0])).count()
        data['month']['timestamp_month'] = list_one
        list_da = []
        da = {}
        da['id'] = h2p(group_name)
        da['count'] = my_work
        da['desc'] = group_name
        list_da.append(da)
        data['sys_count'] = list_da
        data['other'] = other_work
        work__status = list(Work.objects.filter(belong_sys=group_name).filter(
            Q(start_time__lte=list_one[-1]) & Q(start_time__gte=list_one[0])).
                            extra({'name': 'work_status'}).values('name').annotate(value=Count('work_status')))
        data['work_status'] = work__status

    return data


def show_works(time, user):
    if user.is_superuser:

        works = list(Work.objects.filter(Q(build_time__lte=time[-1]) & Q(build_time__gte=time[0])).values().order_by('-id'))

    else:
        group = get_user_group(user)

        works = list(Work.objects.filter(belong_sys=group).filter(Q(build_time__lte=time[-1])
                                                          & Q(build_time__gte=time[0])).values().order_by('-id'))
    return works


def get_publish_work(user):
    if user.is_superuser:
        works = Work.objects.exclude(work_status='未开始').values('belong_sys'). \
            annotate(count=Count('belong_sys')).values('belong_sys', 'count')
    else:
        group = get_user_group(user)
        works = Work.objects.filter(belong_sys=group).exclude(work_status='未开始').count()
    return works


# 根据系统获取系统下的模板
def get_temp_sys(sys):
    temps = Template.objects.filter(belong_sys=sys)
    return temps

def get_temp_sys_env(sys, env):
    temps = Template.objects.filter(Q(belong_sys=sys) & Q(temp_type=env))
    return temps

# 通过模板i查询app和db的ip
def get_ips(temp):

    app_ip = list(Application.objects.filter(temp_id=temp).values())
    # # db_ip = Database.objects.filter(temp_id=temp).values('db_ip')
    # ip_dict = {}
    #
    # app_list = []
    # # db_list = []
    # for i in app_ip:
    #     app_list.append({
    #         'id' : i['id'],
    #         'ip' : i['app_ip'],
    #
    #     }str()+'&nbsp'++':' + )
    # app = order_ip(app_list)
    # ip_dict['app_ip'] = app_list

    # for ii in db_ip:
    #     db_list.append(ii['db_ip'])
    # db = order_ip(db_list)
    # ip_dict['db_ip'] = db
    # 最后需要添加一个排序
    return app_ip


def order_ip(ip_list):
    """
    根据保险公司的ip段，进行ip的自动排序
    :param ip_list: 传入的五个ip字段
    :return: 返回有顺序的ip地址
    """
    return sorted(ip_list, key=socket.inet_aton)


def get_param_value(key, env, group):
    value = json.loads(Config.objects.filter(Q(conf_key=key) & Q(extend1=env) & Q(extend2=group)).
                       values('conf_value')[0]['conf_value'])
    dict_value = {}
    for key, value in value.items():
        dict_value[key] = value
    return dict_value


# 通过前台传值，更新后台的相关数据
def trans_params(trans_list, env, way, sys):
    # 通过传入的list来修改原有数据库中的字段
    param_list = []
    work_params = {}
    for i in json.loads(trans_list):
        little_list = []
        param_list.append(i)
        # 其他步骤
        little_list.append(i['value'])
        little_list.append(i['info'])
        work_params[i['key']] = little_list

    Config.objects.filter(Q(extend1=env) & Q(extend2=sys) & Q(conf_key=way)).\
        update(conf_value=json.dumps(work_params, ensure_ascii=False))


# 通过config的
def judge_path(file_path):
    end = file_path.split('/')[-1]
    if end == '':
        return file_path
    else:
        if '.' in end:
            return file_path
        else:
            file_path += '/'
    return file_path


# 根据value_list 的key来获取value


def get_value(id, key):
    value_list = list(Work.objects.filter(id=id).values('value_list'))
    for i in json.loads(value_list[0]['value_list']):
        if i['key'] == key:
            return i['value']


# 获取时间戳
def get_timestamp():
    return int(time.time())


def insert_log(log, log_list, msg):
    logging.info(msg)
    log_list.append(msg+'\n')
    log.log_info = json.dumps(log_list, ensure_ascii=False)
    log.save(update_fields=['log_info'])


def stop_excute(id):
    work = Work.objects.get(id=id)
    work.work_status = '执行中断'
    work.save()
    return 'success'


def judge_status(id):
    work = Work.objects.get(id=id)
    status = work.work_status
    if status == '执行中断':
        raise RuntimeError('14')


# 获取正在执行中的作业

def get_doing_work(work_type,belong_sys):
    # work_count = Work.objects.filter(Q(work_type=work_type) & Q(work_status='执行中')).count()
    work_count = Work.objects.filter(Q(work_type=work_type) & Q(work_status='执行中') & Q(belong_sys=belong_sys)).count()
    return work_count


# 获取作业名是否存在

def get_same_name(work_name):
    work_name_count = Work.objects.filter(work_name=work_name).count()
    return work_name_count


# 复制模板和里面的内容
def copy_temp(temp_id):
    temp = Template.objects.get(id=temp_id)
    apps = Application.objects.filter(temp_id_id=temp.id)
    # 需要先进行查询
    count = Template.objects.filter(temp_name__contains='副本').count()
    tt = Template.objects.create(temp_name=temp.temp_name+"- 副本"+str(count+1), belong_sys=temp.belong_sys, temp_type=temp.temp_type)
    for app in apps:
        Application.objects.create(app_ip=app.app_ip, hostname=app.hostname, account=app.account, password=app.password,
                                   app_directory=app.app_directory, middleware_name=app.middleware_name, middleware_pass=
                                   app.middleware_pass, url=app.url, upload_path=app.upload_path, port=app.port, log_path=
                                   app.log_path, env_type=app.env_type, temp_id_id=tt.id)


# 获取当前时间距离定时时间的秒间隔
def get_interval_time(time):
    # time = '2018-08-01 20:00:00'
    # print(type(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    aa = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    return (aa - data_now).seconds


def get_work_by(id):

    work = list(Work.objects.filter(id=id).values())
    if '#' in work[0]['time_rule']:
        time = work[0]['time_rule'].split('#')
        work[0]['time_1'] = time[0]
        work[0]['time_2'] = time[1]
    work[0]['value_list'] = json.loads(work[0]['value_list'])
    return work[0]


