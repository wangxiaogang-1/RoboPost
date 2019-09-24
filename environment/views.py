import os, time, json, django

from django.contrib.auth.decorators import login_required

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RoboPost.settings")
django.setup()
import json
import threading
from tool.sshUtil import *
from environment.mysql import *
from tool.execut_work import *
from environment.util import *
from django.db import connection
from environment.loop_time import *
from tool.execut_work import run_task

from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import HttpResponse as httpresponse
from concurrent.futures import ProcessPoolExecutor
from dwebsocket.decorators import accept_websocket


# 登录模块


def test_all(request):
    # # 根据不同的用户获取模板
    # print(get_template(request.user))
    # # 根据模板id获取app和db对象
    # print(get_all_server('1'))
    # # get_works('车险模板')
    return HttpResponse('succ')


# 配置
def configs(request):
    pub, pri = get_template(request.user)
    return render(request, 'environment/configs.html', {
        'pub': pub,
        'pri': pri
    })


# 删除配置
def del_temp(request):
    return HttpResponse(delete_temp(request.POST.get('temp_id')))


# 删除APP服务器
def del_app(request):
    return HttpResponse(delete_application(request.POST.get('app_id')))


# 创建发布任务
def create_issue(request):
    group = get_user_group(request.user)
    env = request.GET.get('env')
    temps = get_temp_sys_env(group, env=env)
    # 根据所选的环境给定不同的参数
    work_params = get_param_value('work_params2', env, group)
    # return render(request, 'environment/createIssue.html', {'temps': temps})
    return render(request, 'environment/createIssue.html', {'temps': temps, 'params': work_params})


# 修改发布任务配置参数
def update_issue(request):
    group = get_user_group(request.user)
    env = request.GET.get('env')
    temps = get_temp_sys_env(group, env=env)
    issue = get_work_by(request.GET.get('work_id'))
    return render(request, 'environment/createIssue.html', {'work': issue, 'temps': temps})


# 执行发布
def view_work(request):
    issue = get_work_by(request.GET.get('work_id'))
    return render(request, 'environment/run.html', {'work': issue})


def run_issue(request):
    work_id = request.GET.get('work_id')
    WK = Work.objects.get(id=work_id)
    if WK.work_status == '未开始':
        WK.work_status = '执行中'
        WK.save(update_fields=['work_status'])
        threading.Thread(target=run_work, args=(request,)).start()
    # 返回作业相关信息到页面
    issue = get_work_by(work_id)
    return render(request, 'environment/run.html', {'work': issue})


def kill_issue(request):
    result = stop_excute(request.POST.get('work_id'))
    return HttpResponse(result)


def del_work(request):
    work_id = request.POST.get('work_id')
    return HttpResponse(delete_work(work_id))


# 根据手动选择获取相应的执行方式参数
def get_params(request):
    group = get_user_group(request.user)
    env = request.POST.get('env')
    return HttpResponse({'params': get_param_value(request.POST.get('publish_way'), env, group)}.__str__())


def get_tempips(request):
    temp_id = request.POST.get('temp_id')
    ips = get_ips(temp_id)
    return HttpResponse({'ips': ips}.__str__())


# 发布概览
def issue(request):
    # 获取模板
    return render(request, 'environment/issue.html')


def issue_data(request):
    works = {'works': show_works(get_30day(int(request.GET.get('time'))), request.user)}
    return render(request, 'environment/issue_data.html', works)


def issue_time_data(request):
    time_list = []
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    time_list.append(int(start))
    time_list.append(int(end))
    works = show_works(time_list, request.user)
    return render(request, 'environment/issue_data.html', {'works': works})


# 创建发布配置模板
def create_config(request):
    data = {
        'systems': get_groups_name(),
        'operate': request.GET.get('operate'),
        'dat': get_temp_by_id(request.GET.get('temp_id')),
        'temps': chose_temp_by_custom(request.user),
        'user_group': get_user_group(request.user)
    }
    return render(request, 'environment/createConfig.html', data)


def copy_temp_v(request):
    copy_temp(request.POST.get('temp_id'))
    return HttpResponse('success')


# 获取模板下的所有配置服务器
def get_taserver(request):
    return HttpResponse({'apps': get_tempappserver(request.POST.get('temp_id'))}.__str__())


# 创建服务器
def cou_appserver_config(request):
    operate = request.GET.get('operate')
    data = {}
    if operate == 'U' or operate == 'V':
        data = get_tAa(request)
    data['operate'] = operate
    return render(request, 'environment/createOrUpdateAppServerConfig.html', data)


# 根据不同的用户展示模板
def show_templates(request):
    pub, pri = get_template(request.user)
    return render(request, 'config/configs.html', {
        'pub': pub,
        'pri': pri
    })


def show_servers_env(request):
    # 通过传递的模板id查询对应的app和db
    apps, dbs = get_server_by_env(request.GET.get('temp'))

    return render(request, 'environment/server.html',
                  {'apps': apps, 'dbs': dbs, 'tmp_type': get_temp_type(request.GET.get('temp'))})


def index(request):
    data = get_servers_account(request)
    return render(request, 'index.html', data)


def get_servers_account(request):
    result = {}
    # 2.车险服务器总数，非车服务器总数，总服务器数（车险 + 非车）
    server_count = get_all_server_account(request.user)
    result['server_count'] = server_count
    all_server_count = server_count.copy()
    for id in range(len(server_count)):
        all_num = all_server_count[id]['count'].split(',')
        all_server_count[id]['count'] = int(all_num[0]) + int(all_num[1])
    result['all_server_count'] = all_server_count
    # 3.车险成功发布任务数，非车成功发布任务数，总任务成功数（车险 + 非车）
    works = get_publish_work(request.user)
    result['works'] = works
    # 4.车险用户数，非车用户数，总用户数（车险 + 非车）
    user_count = get_user_amount(request.user)
    result['user_count'] = user_count
    # 获取30天数据以及任务状态，任务数量统计图
    # 这里需要添加通过时间查询，传递来的使劲戳列表
    data = translate(get_30day(), request.user)
    result['data'] = data
    result['work_list'] = work_list(request.user)[0:10]
    return result


def get30dayline(request):
    data = translate(get_30day(int(request.POST.get('day'))), request.user)
    return HttpResponse(data['month'].__str__())


def get30dateline(request):
    start = int(request.POST.get('start_time'))
    end = int(request.POST.get('end_time'))
    data = translate(show_start_end(start, end), request.user)
    return HttpResponse(data['month'].__str__())


def work_list(user):
    group_name = get_user_group(user)
    if (user.is_superuser):
        wl = list(Work.objects.filter(work_status__in=('执行异常', '执行中断')).values().order_by('-id'))
    else:
        wl = list(Work.objects.filter(work_status__in=('执行异常', '执行中断'), belong_sys=group_name).values().order_by('-id'))
    return wl


def init_work(request):
    # works = json.dumps(show_works(request.user), ensure_ascii=False)
    if request.GET.get('start_time') is not None:
        time_list = []
        start = request.GET.get('start_time')
        end = request.GET.get('end_time')
        time_list.append(int(start))
        time_list.append(int(end))
        works = show_works(time_list, request.user)
    else:
        works = show_works(get_30day(), request.user)

    return render(request, 'environment/init_work.html', {'works': works})


def create_work(request):
    # 获取模板
    group = get_user_group(request.user)
    env = request.POST.get('env')
    temps = get_temp_sys_env(group, env=env)

    # 通过模板的选择获取参数
    return render(request, 'environment/create_work.html', {'temp': temps})


def two_publish_way(request):
    # 手动
    if request.POST.get('S'):
        work_params = get_param_value('work_params')
    # svn
    else:
        work_params = get_param_value('work_params2')
    return HttpResponse(work_params)


def init_ips(request):
    ips = get_ips(request.POST.get('temp_id'))

    return HttpResponse(json.dumps(ips))


def edit_work(request):
    return render(request, 'environment/edit_work.html')


def three_element(work_id):
    log_list = []
    work = Work.objects.get(id=work_id)

    work.work_status = '执行中'
    if work.log_set.filter(work_id=work_id):
        log = Log.objects.get(work_id_id=work_id)
    else:
        log = Log.objects.update_or_create(log_name="作业日志" + str(work_id), log_info=log_list, work_id_id=work_id)[0]
    return log_list, work, log


def check_run(request):
    result = 'can_run'
    work_id = request.POST.get('work_id')
    WK = Work.objects.get(id=work_id)
    doing_work = get_doing_work(WK.work_type, WK.belong_sys)
    if doing_work > 0:
        result = 'failed:系统正在执行发布任务，请稍后执行！'
    return HttpResponse(result);


def run_work(request):

    inner_function(request.GET.get('work_id'))



def inner_function(work_id):

    log_list, work, log = three_element(work_id)
    # 获取时间戳
    work.start_time = get_timestamp()
    work.save(update_fields=['start_time', 'work_status'])
    run_task(work, log, log_list)



def createConfig(request):
    status = request.POST.get('operate')
    temp_id = json.loads(request.POST.get('temp_id'))
    app = json.loads(request.POST.get('application'))
    TEMP = Template.objects.get(id=temp_id)

    if status == 'C':
        app['temp_id_id'] = temp_id
        app['env_type'] = TEMP.temp_type
        create_application(app)
    else:
        app['temp_id_id'] = temp_id
        app['env_type'] = TEMP.temp_type
        update_application(app)

    return HttpResponse(temp_id)


def create_temp_view(request):
    te = json.loads(request.POST.get('temp'))
    status = request.POST.get('operate')
    te['temp_name'] += "_" + te['belong_sys']
    temp_name = te['temp_name']
    count = get_temps_count(temp_name)
    if count > 0:
        return HttpResponse('failed:模板名称已存在！')
    if status == 'C':
        user = request.user
        if user.is_superuser:
            flag = '1'
        else:
            flag = None
        te['extend1'] = flag
        create_temp(te)
    else:
        update_temp(te)
    return HttpResponse('success')


def createConfigUser(request):
    status = request.POST.get('operate')
    te = json.loads(request.POST.get('temp'))
    app = json.loads(request.POST.get('application'))
    if status == 'C':
        user = request.user
        if user.is_superuser:
            flag = '1'
        else:
            flag = None
        te['extend1'] = flag
        temp = create_temp(te)
        tid = temp.id
        app['temp_id_id'] = tid
        app['env_type'] = te['temp_type']
        create_application(app)
    else:
        update_application(app)
        update_temp(te)
        tid = te['id']
    return HttpResponse(tid)


def trans_log(request):
    print('查看执行信息')
    work = Work.objects.get(pk=request.GET.get('work_id'))
    log = Log.objects.get(work_id=work.id)
    # data = {"work_status": work.work_status, "log": log.log_info}
    info = log_filter(log)
    # package_manage()
    data = {"work_status": work.work_status, "log": info}

    return HttpResponse(json.dumps(data))


def log_filter(log):
    """根据前台用户点击要查看的ip,日志过滤本ip下的日志信息"""
    log_info = log.log_info
    logs = eval(str(log_info))
    logs_list = []
    for log in logs:
        #ip根据前台所选进行获取
        if '192.168.43.224' in log or '.' not in log:
            logs_list.append(log)
    log_list = eval(str({}.fromkeys(logs_list).keys())[10:-1])
    return json.dumps(log_list)


def package_manage():
    """包管理,将制定路径下的所有包展示到前台页面,用户选择要删除的包,进行删除"""
    path = '/tmp/'
    dirs = os.listdir(path)
    rm_command = 'cd %s; rm -rf %s' % (path, 'tt')
    r = os.system(rm_command)
    ip = Application.objects.get(id=2)
    conn = sshUtil.create_conn(ip.app_ip, ip.account, ip.password)
    jvm_command = 'su - root'
    res = remote_excu(conn, jvm_command)
    print(res, 'res')

if __name__ == '__main__':
    package_manage()


def create_work_util(request):
    work_dict = request.POST.dict()
    if not work_dict['work_name']:
        return HttpResponse('failed:作业名不可为空！')
    work_dict['extend2'] = eval(work_dict.pop('ipids'))
    if work_dict['extend2'].__len__() == 0:
        return HttpResponse('failed:请至少选择一个服务器来执行！')
    work_dict['belong_sys'] = get_user_group(request.user)
    work_dict['work_status'] = '未开始'
    work_dict['build_time'] = get_timestamp()
    work_dict['jar_name'] = None if work_dict['publish_way'] == 'work_params' else work_dict['jar_name']
    work_id = work_dict.pop('id')
    if work_id:
        Work.objects.filter(id=work_id).update(**work_dict)
        work = Work.objects.get(id=work_id)
    else:
        if get_same_name(work_dict['work_name']) > 0:
            return HttpResponse('failed:作业名称已经存在！')
        work = Work.objects.create(**work_dict)
    trans_params(work_dict['value_list'], work_dict['work_type'], work_dict['publish_way'], work_dict['belong_sys'])
    if get_time(work_id):
        rem_time(work_id)
    if work_dict['run_way'] == '定时':
        # 需要另一种指定定时的方式
        timer = work.time_rule.split('#')
        add_one_time(inner_function, work.id, work.id, timer[0])
    return HttpResponse('success')


def timesleep(second):
    time.sleep(int(second[0]))


def upload_zip(request):
    try:
        # 可以获取上传文件的文件名
        tool_file = request.FILES.get('file')
        # 指定临时文件写入路径
        # 本地路径 直接通过前台传递
        file_path = PUBLIC_DIR
        # 这里写入文件后一定要关闭，要不然下面会读取不到
        f = open(os.path.join(file_path, tool_file.name), 'wb')
        for chunk in tool_file.chunks(chunk_size=1024):
            f.write(chunk)
        f.close()
        result = 'success'
    except Exception as e:
        result = 'failed'
    return HttpResponse(result)


# 创建一个方法，可以根据作业创建作业
def roll_back_view(request):
    # 作业id
    work_id = request.GET.get('work_id')
    work = Work.objects.get(id=work_id)
    if work.extend1:
        return HttpResponse('该任务无法回滚！')
    if not work.webapps_name:
        return HttpResponse('该作业没有进行webapps备份,无法回滚！')
    work.extend1 = '回退开始'
    work.work_status = '执行中'
    work.save(update_fields=['extend1', 'work_status'])
    log = Log.objects.get(work_id=work_id)
    threading.Thread(target=run_task, args=(work, log, eval(log.log_info))).start()
    workk = get_work_by(work_id)
    return render(request, 'environment/run.html', {'work': workk})


def read_file(size, sourcefile, targetfile, loop):
    '''

    :param size: 读取文件的行数
    :param sourcefile: 源文件路径
    :param targetfile: 商户处文件路径
    :param loop:
    :return:
    '''

    f = open(sourcefile, 'r', encoding='utf-8')
    content = f.readlines()[(0 + loop) * size:(loop + 1) * size]
    ff = open(targetfile, 'w')
    ff.writelines(content)


def yield_test():
    for i in range(1, 10000):
        yield i


