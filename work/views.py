from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime
import time
from datetime import timedelta
from confManage.views import getPublicParameterKeyword, getHostInfoId
from tool.constant import SystemConfigs as CONFIG
from confManage.views import get_config_locator
from confManage.models import PublicParameter
from django.shortcuts import render
from django.shortcuts import HttpResponse
from work.models import *
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from tool.timing import *
from confManage import models
from tool.sshUtil import get_user_ip
from tool.workUtil import getlog
from tool.data_tool import queryset_transducer
from dwebsocket.decorators import accept_websocket
from tool.workUtil import runwork
import threading
from tool.model import card_model
import copy
log = logging.getLogger('autoops')
QUERYSET_FIRST_ELEM = CONFIG.QUERYSET_FIRST_ELEM


@login_required(login_url='/')
def works(request):
    work_list = WorkInfo.objects.all().order_by('-id')
    log.info(get_user_ip(request) + '进入作业模块')
    return render(request, 'work/works.html', {'data': work_list})


@login_required(login_url='/')
def run_work_single(request):
    work_id = int(request.GET.get('wid'))
    work = get_work_for_show(work_id)
    if work['work_status'] == 0:
        threading.Thread(target=runwork, args=(request, work_id,)).start()
    return render(request, 'work/runWork.html', {'work': work})


@login_required(login_url='/')
def run_work(request):
    ids = request.POST.get('work_ids').split(',')
    for work_id in ids:
        threading.Thread(target=runwork, args=(request, int(work_id),)).start()
    return HttpResponse('success')


@login_required(login_url='/')
def run_work_time(request, workid):
    threading.Thread(target=runwork, args=(request, int(workid),)).start()
    return HttpResponse('success')


@login_required(login_url='/')
def show_work(request):
    work_id = int(request.GET.get('wid'))
    work = get_work_for_show(work_id)
    return render(request, 'work/runWork.html', {'work': work})


def get_work_for_show(work_id):
    work = queryset_transducer(WorkInfo.objects.filter(id=work_id).values())[QUERYSET_FIRST_ELEM]
    ips = []
    for id in work['host_list'].split(','):
        ips.append(getHostInfoId(id).IP)
    work['host_list'] = ips
    return work


@login_required(login_url='/')
def selectPackage(request):
    data = upload(request)
    return render(request, 'work/selectPackage.html', {'files': data})


@login_required(login_url='/')
def upload(request):
    log.info(get_user_ip(request) + "遍历本地公共目录，获取zip文件")
    dir_o = PublicParameter.objects.get(confK='local_public_dir')
    path = dir_o.confV
    fs = os.listdir(path)
    list_files = []
    for f1 in fs:
        tmp_path = os.path.join(path, f1)
        if not os.path.isdir(tmp_path):
            print('文件: %s' % tmp_path)
            list_files.append(tmp_path)
            log.info(get_user_ip(request) + '文件: %s' % tmp_path)
        else:
            print('文件夹：%s' % tmp_path)
            log.info(get_user_ip(request) + '文件夹：%s' % tmp_path)
    return sorted(list_files)

def upload_zip(request):
    log.info(get_user_ip(request) + "页面上传zip文件的方法")
    if request.method == 'POST':
        # 可以获取上传文件的文件名
        tool_file = request.FILES.get('file')
        # 指定临时文件写入路径
        file_path = 'static/zips/'
        # 这里写入文件后一定要关闭，要不然下面会读取不到
        f = open(os.path.join(file_path, tool_file.name), 'wb')
        for chunk in tool_file.chunks(chunk_size=1024):
            f.write(chunk)
        f.close()

        result = 'success'
        log.info(get_user_ip(request) + "zip文件上传success")
    else:
        result = 'failed'
        log.info(get_user_ip(request) + "zip文件上传failed")
    return HttpResponse(result)


def ppp(province, platform, project, five_list):
    # 获取初始化数据

    param_dict = {}
    # 获取机器表的数据
    data = models.HostInfo.objects.filter(province=province, platform=platform,
                                          project=project).values()
    param_list = []
    app_machine_ips = ""
    app_machine_users = ""
    app_machine_pwds = ""
    urls = ""
    app_application_dir = ""
    app_html_dir = ""
    app_cache_dir = ""
    app_restart_dir_name = ""

    for i in list(data):
        list_dict = {}
        # 通过省市，平台，项目定位的Host_info的id有两个
        ids = i['id']
        db = list(models.DBInfo.objects.filter(host_ip=ids).values())
        pj = list(models.ProjectInfo.objects.filter(host_ip=ids).values())

        if db.__len__() != 0:

            host_db = list(models.HostInfo.objects.filter(id=db[0]['host_ip_id']).values())[0]
            param_list.append({"key": "database_machine_user", "value": host_db['account'], "info": "数据库对应机器用户名"})
            param_list.append({"key": "database_machine_pwd", "value": host_db['password'], "info": "数据库对应机器密码"})
            param_list.append({"key": "database_ip", "value": host_db['IP'], "info": "数据库对应机器IP"})
            for ii in db:
                param_list.append({"key": "database_name", "value": ii['name'], "info": "数据库名称"})
                param_list.append({"key": "database_user", "value": ii['account'], "info": "数据库用户名"})
                param_list.append({"key": "database_pwd", "value": ii['password'], "info": "数据库密码"})
                param_list.append({"key": "tns_name", "value": ii['tnsname'], "info": "数据库别名"})

        if pj.__len__() != 0:
            host_pj = list(models.HostInfo.objects.filter(id=pj[0]['host_ip_id']).values())
            for host in host_pj:
                app_machine_ips += host['IP'] + ','
                app_machine_users += host['account'] + ','
                app_machine_pwds += host['password'] + ','
            for ppjj in pj:
                app_application_dir += ppjj['app_directory'] + ","
                app_html_dir += ppjj['static_directory'] + ","
                app_cache_dir += ppjj['cache_directory'] + "@"
                app_restart_dir_name += ppjj['restart_script_path'] + ","
                urls += ppjj['url'] + ','
    param_list.append({"key": "app_machine_ip", "value": app_machine_ips[:-1], "info": "应用机器IP"})
    param_list.append({"key": "app_machine_user", "value": app_machine_users[:-1], "info": "应用机器用户名"})
    param_list.append({"key": "app_machine_pwd", "value": app_machine_pwds[:-1], "info": "应用机器密码"})
    param_list.append({"key": "url", "value": urls[:-1], "info": "应用机器访问地址"})
    param_list.append({"key": "app_application_dir", "value": app_application_dir[:-1], "info": "应用项目路径"})
    param_list.append({"key": "app_html_dir", "value": app_html_dir[:-1], "info": "应用静态文件夹路径"})
    param_list.append({"key": "app_cache_dir", "value": app_cache_dir[:-1], "info": "应用缓存文件夹路径"})
    param_list.append(
        {"key": "app_restart_dir_name", "value": app_restart_dir_name[:-1], "info": "应用重启文件夹路径"})
    work_params = {}
    print(five_list)
    print(type(five_list))
    for i in json.loads(five_list):
        little_list = []
        param_list.append(i)
        # 其他步骤
        little_list.append(i['value'])
        little_list.append(i['info'])
        work_params[i['key']] = little_list

    models.PublicParameter.objects.filter(id='15').update(confV=json.dumps(work_params, ensure_ascii=False))
    return json.dumps(param_list, ensure_ascii=False)


@login_required(login_url='/')
def createOrUpdateWorkPage(request):
    # 获取初始化数据
    cl = get_config_locator()
    cl['runway'] = getPublicParameterKeyword(keyword='runway')[QUERYSET_FIRST_ELEM]['confV'].split(',')

    return render(request, 'work/createOrUpdateWork.html', cl)


@login_required(login_url='/')
def createOrUpdateWork(request):
    result = 'success'
    work = {}
    for key in request.POST:
        work[key] = request.POST.get(key)
    five_list = request.POST.get('value_list')

    file_package_names = request.POST.get('file_package_names')
    work['file_package_names'] = file_package_names.replace(' ', '')
    if work['id'] != '':
        result = updateWorkinfo(request, work)
        return HttpResponse(result)
    work.pop('id')
    value_list = ppp(work['province'], work['platform'], work['project'], five_list)

    work['value_list'] = value_list

    work_saved = WorkInfo.objects.create(**work)
    log.info(get_user_ip(request) + "作业创建成功！，作业ID为:" + str(work_saved.id))
    # 添加定时

    if work['time_rule'] != '':
        # 加入定时
        add_time(run_work_time, args=(request, work_saved.id), id=work_saved.id, time=work['time_rule'])
        log.info(get_user_ip(request) + "作业创建定时成功！，作业ID为:" + str(work_saved.id) + ",定时规则为：" + work['time_rule'])

    if work_saved is None:
        result = 'failed'

    return HttpResponse(result)


@login_required(login_url='/')
def initUpdateWork(request):
    cl = get_config_locator()
    cl['runway'] = getPublicParameterKeyword(keyword='runway')[QUERYSET_FIRST_ELEM]['confV'].split(',')
    workId = request.GET.get('wid')
    cl['work'] = queryset_transducer(WorkInfo.objects.filter(id=workId).values())[QUERYSET_FIRST_ELEM]
    cl['work']['value_list'] = json.loads(cl['work']['value_list'])
    h_list = []
    for hostId in cl['work']['host_list'].split(','):
        h_list.append(getHostInfoId(hostId))
    cl['work']['host_list'] = h_list
    return render(request, 'work/createOrUpdateWork.html', cl)


def updateWorkinfo(request, workinfo):
    result = 'failed'
    wid = workinfo['id']
    workinfoUpdated = WorkInfo.objects.filter(id=wid).update(**workinfo)
    if workinfoUpdated is not None:
        result = 'success'
        log.info(get_user_ip(request) + "作业更新成功！，作业ID为:" + workinfo['id'])
        if workinfo['time_rule'] != '':
            # 删除定时
            if get_time(id=workinfo['id']) is not None:
                vv = get_time(id=workinfo['id'])

                rem_time(id=workinfo['id'])
                log.info(get_user_ip(request) + "删除原有定时成功！，定时ID为:" + workinfo['id'] + ',时间为:' + str(vv.trigger))
            # 重新定时
            add_time(run_work_time, args=(request, workinfo['id']), id=workinfo['id'], time=workinfo['time_rule'])
            log.info(get_user_ip(request) + "作业更新定时成功！，作业ID为:" + workinfo['id'] + ',定时规则为：' + workinfo['time_rule'])
    return result


# 考虑到的，作业增删改查，复制，中断，
@login_required(login_url='/')
def test_print(request, s):
    return HttpResponse('aa')


@login_required(login_url='/')
def test_add_time(request):
    """
    添加定时，要求有任务id，定时需要时字符串类型的列表，以及需要确定执行方法传递的参数即可
    项目重启后，没有达到执行时间的任务需要重新执行，可以从数据库中获取数据，再添加到定时任务即可
    :param request:
    :return:
    """
    # time = "[0, 2, 14, 20, 3]"
    # s = add_time(test_print, args=('a', 'b'), id=1, time=time)
    # # 只要保持他们调用的对象一致，就可以获取定时任务。以及所以任务，并进行操作
    # print(s.id)
    # print(scheduler.get_jobs())

    return HttpResponse('add_job')


@login_required(login_url='/')
def test_del_time(request):
    get = get_time('1')
    return HttpResponse('remove_job_success')


# 删除作业
@login_required(login_url='/')
def delete_work(request):
    """
    :param request: Django request对象
    :return: 返回删除或失败的状态到前台
    """

    if request.method == 'POST':
        id_list = request.POST.getlist('ids')
        ids = id_list[0].split(',')
        for id in ids:
            WorkInfo.objects.filter(id=id).delete()
            loginfo = WorkLog.objects.filter(work_id=id)
            if (loginfo):
                loginfo.delete()
                log.info(get_user_ip(request) + "删除作业连带日志公成功，作业ID为:" + str(id))
            log.info(get_user_ip(request) + "删除作业成功，作业ID为:" + str(id))
            if get_time(id=str(id)) is not None:
                vv = get_time(id=str(id))

                rem_time(id=str(id))
                log.info(get_user_ip(request) + "删除原有定时成功！，定时ID为:" + str(id) + ',时间为:' + str(vv.trigger))

        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 中断作业的方法
@login_required(login_url='/')
def stop_work(request):
    # 中断作业需要知道作业的id
    id = request.POST.get('work_id')
    # 同时这里使用的中断是将当前任务正在执行的脚本执行完毕，所以是否存在中断后无法立即处理的问题？
    WorkInfo.objects.filter(id=id).update(work_status=3)
    log.info(get_user_ip(request) + "作业中断成功，作业ID为:" + id)
    # 同时涉及批量中断，那就需要获取多个id，
    # 中断也就是远程的执行，只不过将执行取消掉而已
    return HttpResponse('success')


def make_page(request, data, number, page):
    """
    :param request: request对象
    :param data: 数据
    :param number: 分页页数
    :param page: 前台传来的page数量
    :return:返回分页后的数据
    """
    # 需要列表类型数据，number每页显示数据
    paginator = Paginator(list(data), number)
    # 通过GET请求获取页数

    try:
        # 传过来多少页 就显示第几页
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 传递的不是数字就显示第一页
        contacts = paginator.page(1)
    except EmptyPage:
        # 传递的是空
        contacts = paginator.page(paginator.num_pages)
    return contacts


# 复制作业
def copy_work(request):
    log.info("复制作业")
    ids = request.POST.get('workIds').split(',')
    for workId in ids:
        copy = WorkInfo.objects.filter(id=workId).values_list('id', 'workname', 'platform',
                                                              'orderlist', 'workinfo',
                                                              'runway', 'timingrules',
                                                              'starttime', 'founder',
                                                              'endtime',
                                                              'runuser', 'workstatus',
                                                              'runstatus', 'extend1')
        taskId_list = copy[3].split(',')

    return HttpResponse('success')


@login_required(login_url='/')
@accept_websocket
def send_log(request):
    workid = request.GET.get('work_id')
    workinfo = WorkInfo.objects.get(pk=workid)
    data = {
        "work_status": None,
        "log": ""
    }
    tag = 1
    if workinfo.work_status != 1:
        while tag:
            data["work_status"] = workinfo.work_status
            data["log"] = json.dumps(getlog(workid), ensure_ascii=False)
            request.websocket.send(str(data).encode('utf-8'))
            time.sleep(2)
            tag =0
    else:
        while workinfo.work_status == 1:
            workinfo = WorkInfo.objects.get(pk=workid)
            data["work_status"] = workinfo.work_status
            data["log"] = json.dumps(getlog(workid), ensure_ascii=False)
            request.websocket.send(str(data).encode('utf-8'))


def get_project(request):
    data = {"card": {}}
    # 统计各个项目数量
    proj = list(WorkInfo.objects.all().values('project').annotate(count=Count('project')).
                values('project', 'count'))
    data['card']['project'] = []
    active_flag = True
    for p in proj:
        cp_proj_model = copy.deepcopy(card_model['project']['default'])
        if active_flag:
            cp_proj_model['status'] = 'active'
            active_flag = False
        cp_proj_model['count'] = p['count']
        cp_proj_model['label'] = p['project']
        data['card']['project'].append(cp_proj_model)
    # 获得服务器总数，应用和数据库
    host = list(models.HostInfo.objects.all().values('server_type').annotate(count=Count('server_type')). \
                values('server_type', 'count'))
    count = 0
    for i in host:
        count += i['count']
    host.append({'server_type': 'all', 'count': count})
    data['card']['host'] = []
    for h in host:
        card_model['host'][h['server_type']]['count'] = h['count']
        data['card']['host'].append(card_model['host'][h['server_type']])

    work_list = []
    work_all = WorkInfo.objects.all().count()
    work_success = WorkInfo.objects.filter(work_status=2).count()
    work_error = WorkInfo.objects.filter(work_status=4).count()
    work_list.append({'work_status': 'all', 'count': work_all})
    work_list.append({'work_status': 'success', 'count': work_success})
    work_list.append({'work_status': 'failed', 'count': work_error})
    data['card']['work'] = []
    for work in work_list:
        card_model['work'][work['work_status']]['count'] = work['count']
        data['card']['work'].append(card_model['work'][work['work_status']])
    # 获取用户数量
    user_list = []
    user = User.objects.all().count()
    user_list.append({'name': 'all', 'count': user})
    data['card']['user'] = []
    for user in user_list:
        card_model['user'][user['name']]['count'] = user['count']
        data['card']['user'].append(card_model['user'][user['name']])

    # 获得作业中项目的种类和数量
    work_count_proj = []
    statistics_workp = list(
        WorkInfo.objects.all().extra(select={'name': 'project'}).values('name').annotate(value=Count('project')).
            values('name', 'value'))
    statistics_workp_names = list(WorkInfo.objects.all().extra(select={'name': 'project'}).values('name').distinct())
    data['statistics_workp_names'] = statistics_workp_names
    data['statistics_workp'] = statistics_workp
    # 统计各个状态作业
    # 作业总数，完成总数，失败总数
    statistics_works = list(WorkInfo.objects.all().extra(select={'name': 'work_status'}).values('name').annotate(
        value=Count('work_status')).
                            values('name', 'value'))
    statistics_works_names = list(WorkInfo.objects.all().extra(select={'name': 'work_status'}).values('name'))
    status_code = PublicParameter.objects.get(confK='work_status');
    status_code = status_code.confV.split(',');
    for sw in statistics_works:
        sw['name'] = status_code[int(sw['name'])]
    for swn in statistics_works_names:
        swn['name'] = status_code[int(swn['name'])]
    data['statistics_works_names'] = statistics_works_names
    data['statistics_works'] = statistics_works
    # 30天
    list_one = get_day()
    data['month'] = {}
    data['month']['data_success'], data['month']['data_error'], data['month']['timestamp_month'] = [], [], []
    for i in list_one:
        success = WorkInfo.objects.filter(work_status=2).filter(start_time__lte=i).filter(
            start_time__gte=i - 86400).count()
        error = WorkInfo.objects.filter(work_status=4).filter(start_time__lte=i).filter(
            start_time__gte=i - 86400).count()
        data['month']['data_success'].append(success)
        data['month']['data_error'].append(error)
    data['month']['timestamp_month'] = list_one
    data['works'] = get_success_error();
    return data


def get_day():
    tm = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # str
    now = datetime.datetime.strptime(str(tm), "%Y-%m-%d %H:%M:%S")  # datetime.datetime

    # 循环
    list_one = []
    count = 1
    list_one.append(int(now.timestamp()))
    while count <= 29:
        day = now - timedelta(days=count)
        list_one.append(int(day.timestamp()))
        count += 1
    list_one.reverse()
    return list_one


def get_success_error():
    works = list(WorkInfo.objects.all().filter(work_status__in=(1, 4)).values())
    return works

def upload_mutifile(request):
    log.info((get_user_ip(request) + "进入上传方法"))

    files = request.FILES.getlist('fileList')
    x = getPublicParameterKeyword('work_param')[0]['confV']
    file_path = ''
    for key, value in (json.loads(x)).items():
        if key == 'local_public_dir':
            # 获取路径
            file_path = value[0]
    directory = os.listdir(file_path)
    for file in files:

        # if str(file) in directory:
        #     # print('文件已存在，是否要替换文件:' + str(file))
        #     return HttpResponse('exists')
        # 将上次文件写入路径
        f = open(os.path.join(file_path, file.name), 'wb')
        for chunk in file.chunks(chunk_size=1024):
            f.write(chunk)
        f.close()
    return HttpResponse('success')
