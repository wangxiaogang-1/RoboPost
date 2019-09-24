
import traceback
import threading
from tool import sshUtil

from environment.util import *
from django.db import connection
from environment.config import config_dict
from concurrent import futures
from concurrent.futures import wait as waiting
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED
from environment.config import PUBLIC_DIR
from pyecharts.charts import Bar, Radar, Line, Page
from pyecharts import options as opts
from pyecharts.faker import Faker


def run_task(work, log, log_list):
    # 在这里做判断，是jar包上传的执行方式，还是svn的更新方式publish_way进行判断
    insert_log(log, log_list, '开始执行任务')
    file = work.jar_name
    ips_all = eval(work.extend2)
    # 直接执行列表
    first_list = []
    # 特殊执行列表
    wait_list = []
    # 去重复列表
    distinct_dict_back = {}
    distinct_dict_start = {}
    # 回滚列表
    roll_dict = {}
    for old in ips_all:
        ip = get_one_server(old['id'])
        roll_dict[ip.app_ip] = ip
        if old['status'] == '0' or old['status'] == '2':
            distinct_dict_back[ip.app_ip] = ip
        if ('-2'in ip.hostname) or ('2' in ip.hostname):
            # 添加等待的ip
            distinct_dict_start[ip.app_ip] = ip
            wait_list.append(old)
        else:
            # 添加无需等待的ip
            distinct_dict_start[ip.app_ip] = ip
            first_list.append(old)
    # new_distinct_list = list(set(distinct_list))
    # 首次执行的组
    backup_list = [v for k, v in distinct_dict_back.items()]
    start_list = [v for k, v in distinct_dict_start.items()]
    endflag = 'echo $?'
    try:
        if not backup_list and file:
            with ThreadPoolExecutor() as executer:
                tasks = [executer.submit(un_jar, log, log_list, sshUtil. create_conn(i.app_ip, i.account, i.password),
                                         PUBLIC_DIR, judge_path(i.upload_path), endflag, file
                                         , i.app_ip) for i in start_list]
                waiting(tasks, timeout=None, return_when=ALL_COMPLETED)
                done_iter = futures.as_completed(tasks)  # generator
                for done in done_iter:
                    print(done.result())

        if not work.extend1:
            time_now = datetime.now().strftime('%Y%m%d%H%M%S')
            with ThreadPoolExecutor() as executer:
                tasks = [executer.submit(one_end, PUBLIC_DIR,
                                         i.app_ip, sshUtil.create_conn(i.app_ip, i.account, i.password),
                                         judge_path(i.upload_path), work, log, log_list, file,
                                         i.extend1, time_now, endflag) for i in backup_list]
                waiting(tasks, timeout=None, return_when=ALL_COMPLETED)
                done_iter = futures.as_completed(tasks)  # generator
                for done in done_iter:
                    print(done.result())
        else:
            insert_log(log, log_list, '服务器: %s开始进行回滚操作！！！' % ip)
            # 回滚操作
            roll_list = [v for k, v in roll_dict.items()]
            with ThreadPoolExecutor() as executer:
                tasks = [executer.submit(roll_webapps, i.app_ip, i.account, i.password,
                                         judge_path(i.upload_path), work, log, log_list) for i in roll_list]
                waiting(tasks, timeout=None, return_when=ALL_COMPLETED)
                done_iter = futures.as_completed(tasks)  # generator
                for done in done_iter:
                    print(done.result())
            work.extend1 = '回退成功'
            work.save(update_fields=['extend1'])
            insert_log(log, log_list, '服务器回滚操作全部完成,开始进行服务器启停操作')

        # 备份解压组
        # 首次执行启停组
        if first_list.__len__():
            insert_log(log, log_list, '第一批服务器开始进行升级操作！！！')
            with ThreadPoolExecutor() as executer:
                tasks = [executer.submit(copy_stop_start, i, log, log_list, work, backup_list, file) for i in first_list]
                waiting(tasks, timeout=None, return_when=ALL_COMPLETED)
                done_iter = futures.as_completed(tasks)  # generator
                for done in done_iter:
                    print(done.result())

        # 等待执启停组
        if wait_list.__len__():
            insert_log(log, log_list, '第二批服务器开始进行升级操作！！！')
            with ThreadPoolExecutor() as executer:
                tasks = [executer.submit(copy_stop_start, i, log, log_list, work, backup_list, file) for i in wait_list]
                waiting(tasks, timeout=None, return_when=ALL_COMPLETED)
                done_iter = futures.as_completed(tasks)  # generator
                for done in done_iter:
                    print(done.result())

        insert_log(log, log_list, '当前任务下所有服务器执行命令完成,任务执行成功(^_^)"!')
        work.work_status = '回退成功' if work.extend1 == '回退成功' else '执行成功'
        work.end_time = get_timestamp()
        work.save(update_fields=['work_status', 'end_time'])
    except Exception as e:
        insert_log(log, log_list, traceback.format_exc())
        if str(e) in config_dict.keys():
            info = config_dict[str(e)]
            insert_log(log, log_list, info[0])
        work.work_status = '执行异常'
        work.end_time = get_timestamp()
        work.save(update_fields=['end_time', 'work_status'])
        django.db.connection.close()


def copy_stop_start(i, log, log_list, work, backup_list, file):
    endflag = 'echo $?'
    ip = get_one_server(i['id'])

    # if not backup_list and file:
    #     un_jar(log, log_list, sshUtil.create_conn(ip.app_ip, ip.account, ip.password),
    #            PUBLIC_DIR, judge_path(ip.upload_path), endflag, file, ip.app_ip)

    insert_log(log, log_list, '##############################')
    insert_log(log, log_list, '当前机器ip为:' + ip.app_ip + '###')
    insert_log(log, log_list, '##############################')
    # 只进行启停
    try:
        if i['status'] == '1' or i['status'] == '0':
            insert_log(log, log_list, '服务器：%s %s开始进行启停weblogic操作！' % (ip.app_ip, ip.port))
            stop_way(work, log, log_list, sshUtil.create_conn(ip.app_ip, ip.account, ip.password),
                    ip.app_directory, ip.log_path, endflag, ip.port, ip.app_ip,)
        else:
            insert_log(log, log_list, '服务器：%s %s 该机器不参与启停操作' % (ip.app_ip, ip.port))
    except Exception as e:
        raise e


def log_check_way(check_log, log, log_list, work):
    ip = get_one_server(check_log['id'])
    conn = sshUtil.create_conn(ip.app_ip, ip.account, ip.password)
    check_console_other(log, log_list, work, ip.app_ip, ip.port, conn)


def backup_multil_path(backup, web, webapps_time, log, log_list, upload_path, endflag, conn, ip, count, work):
    name = judge_path(backup) + web + webapps_time
    insert_log(log, log_list, '服务器：%s 备份文件路径为：%s,备份后的路径为：%s' % (ip, backup, name))
    # cp_command = 'cd %s ;cp -r %s %s%s ;%s' % (upload_path, name, name, webapps_time, endflag)
    source_web = upload_path + web
    cp_command = 'cp -r %s %s;%s ' % (source_web, name, endflag)
    result = sshUtil.my_remote_execute(conn, cp_command)
    if count == 1:
        if not work.webapps_name:
            work.webapps_name = name
            work.save(update_fields=['webapps_name'])
    if result != '0':

        raise RuntimeError('8')
    else:
        insert_log(log, log_list, '服务器：%s 文件备份成功，文件名为:%s' % (ip, name))


def one_end(public_dir, ip, conn, upload_path, work, log, log_list, file, backup_path, webapps_time, endflag):
    insert_log(log, log_list, '服务器: %s 开始进行备份操作！！！' % ip)
    insert_log(log, log_list, '服务器：%s 开始进行备份操作,备份路径为：%s' % (ip, upload_path))
    insert_log(log, log_list, '服务器：%s 开始建立远程连接' % ip)
    insert_log(log, log_list, '服务器：%s 备份文件,备份时间: %s' % (ip, webapps_time))
    web = get_value(work.id, 'webapp_name')
    # 如果有备份路径使用备份路径
    if backup_path:
        backup_list = backup_path.split('#')
        count = 1
        for backup in backup_list:
            threading.Thread(target=backup_multil_path, args=(backup, web, webapps_time,
                             log, log_list, upload_path, endflag, conn, ip, count, work,)).start()
            count += 1
    # # 如果没有直接在上传路径下备份
    # else:
    #     name = upload_path+web+webapps_time
    #     insert_log(log, log_list, '服务器：%s 备份文件路径为：%s,备份后的路径为：%s' % (ip, backup_path, name))
    #     source_web = upload_path+web
    #     cp_command = 'cp -r %s %s;%s ' % (source_web, name, endflag)
    #     result = sshUtil.remote_excu(conn, cp_command)
    if file:
        un_jar(log, log_list, conn, public_dir, upload_path, endflag, file, ip)


def un_jar(log, log_list, conn, public_dir, upload_path, endflag, file, ip):
    insert_log(log, log_list, '将打包文件上到到远程公共目')
    # 如果路径没有错
    if sshUtil.my_remote_execute(conn, 'cd %s; %s' % (upload_path, endflag)) == '0':
        sshUtil.remote_upload(conn, public_dir + file, upload_path + file)
        insert_log(log, log_list, 'jar包成功上传至目标机器' + ip + '路径为:' + upload_path)
    else:
        raise RuntimeError('4')
    insert_log(log, log_list, '开始解压文件进行增量升级')
    command = 'cd %s;jar -xvf %s;%s' % (upload_path, file, endflag)
    # command = 'cd %s;/opt/bea/jdk142_11/bin/jar -xvf %s;%s' % (upload_path, file, endflag)
    unjar = sshUtil.my_remote_execute(conn, command)

    # 这句话可以作为日志进行输出打印！
    if unjar[-1] != '0':
        raise RuntimeError('9')
    else:
        insert_log(log, log_list, unjar)


def kill_way(conn, log, log_list, endflag, port, ip):
    insert_log(log, log_list, '服务器：%s 的端口号为:%s' % (ip, port))
    insert_log(log, log_list, '服务器：%s 查看进行pid，并杀掉进程' % ip)
    # 这个方法单独执行找不到jar因此要加入 刷新系统环境变量
    check_command = "lsof -i:%s |awk '{print $2}'|xargs | awk '{print $2}'" % port
    # pid = sshUtil.remote_excu(conn, check_command)
    pid = sshUtil.my_remote_execute(conn, check_command)
    if pid:
        order = "kill -9 %s ; %s" % (pid, endflag)
        # result = sshUtil.remote_excu(conn, order)
        result = sshUtil.my_remote_execute(conn, order)
        if result != '0':
            insert_log(log, log_list, '服务器：%s 端口为: %s的进程终止失败' % (ip, port))
        else:
            insert_log(log, log_list, '服务器：%s 进程号为:%s的进程。中断成功' % (ip, pid))
    else:
        insert_log(log, log_list, '服务器：%s 没有查询到:%s的端口号, 进程中断失败！' % (ip, pid))


def stop_way(work, log, log_list, conn, weblogic_dir, log_path, endflag, port, ip):
    # 6停止进程，通过停止的输出内容进行判断！
    kill_way(conn, log, log_list, endflag, port, ip)
    # 7进入日志目录并清除缓存
    # sshUtil.remote_excu(conn, "cd %s;%s" % (log_path, endflag))
    sshUtil.my_remote_execute(conn, "cd %s;%s" % (log_path, endflag))
    dangerous_list = []
    if log_path:
        dangerous = ['/bin',  '/boot',  '/dev',  '/etc',  '/home',
                     '/lib',  '/lib64',  '/lost+found',  '/media',
                     '/misc',  '/mnt',  '/net',  '/opt',  '/proc',
                     '/root',  '/sbin',  '/selinux',  '/srv',  '/sys',
                     '/tmp',  '/usr',  '/var']

        for path in dangerous:
            if log_path == path or log_path == path + '/':
                dangerous_list.append(log_path)

        if dangerous_list:
            insert_log(log, log_list, '服务器：%s,日志缓存目录为危险路径：%s ,请检查后进行修改！' % (ip, log_path))
        else:
            insert_log(log, log_list, '进入服务器：%s 日志缓存目录为：%s并清除缓存' % (ip, log_path))
            # sshUtil.remote_excu(conn, "cd %s; rm -rf *;%s" % (log_path, endflag))
            sshUtil.my_remote_execute(conn, "cd %s; rm -rf *;%s" % (log_path, endflag))
            insert_log(log, log_list, '服务器: %s清除缓存成功' % ip)
    # 判断work_status
    insert_log(log, log_list, 'nohup启动%s %s 的weblogic服务器' % (ip, port))
    # sshUtil.remote_excu(conn, 'nohup %s > %s/nohup.out 2>&1 &' % (weblogic_dir, weblogic_dir[:weblogic_dir.rfind('/')+1]))
    sshUtil.my_remote_execute(conn, 'nohup %s > %s/nohup.out 2>&1 &' % (weblogic_dir, weblogic_dir[:weblogic_dir.rfind('/') + 1]))
    check_console_other(log, log_list, work, ip, port, conn)
    insert_log(log, log_list, '%s %s 的服务器所有操作流程执行完毕！！！' % (ip, port))


# def roll_back(work):
#     log = Log.objects.get(work_id=work.id)
#     log_list = eval(log.log_info)
#     apps = (eval(work.extend2))
#     insert_log(log, log_list, '开始进行回退操作。')


def roll_webapps(ip, account, password, upload_path, work, log, log_list):
    time_now = datetime.now().strftime('%Y%m%d%H%M%S')

    backup_path = work.webapps_name
    webapp_name = 'webapps'
    web = backup_path[backup_path.rfind('/')+1:]
    insert_log(log, log_list, '服务器：%s 开始进行回退操作!' % ip)
    insert_log(log, log_list, '服务器：%s 开始建立远程连接' % ip)
    try:
        conn = sshUtil.create_conn(ip, account, password)
    except Exception as e:
        print(e)
        raise RuntimeError('3')
    #######################################
    command = 'cd %s;ls' % upload_path
    result = sshUtil.my_remote_execute(conn, command)
    dir_list = result.split('\n')
    flag = True
    for dir in dir_list:
        if web == dir:
            insert_log(log, log_list, 'jar包上传路劲已经存在webapps的备份包，无需备份')
            flag = False
    # 1.首先取备份路径下看是否存在该备份文件，如果不存在，则复制过来
    if flag:
        # 2.将备份目录文件移动到应用目录
        cp_command = 'cp -r %s %s' % (backup_path, upload_path+web)
        insert_log(log, log_list, '%s :服务器将备份目录文件%s移动到应用目录%s' % (ip, backup_path, upload_path+web))
        result = sshUtil.my_remote_execute(conn, cp_command)
        insert_log(log, log_list, '%s :服务器%s' % (ip, result if result else '复制文件成功'))
        if not result:
            mv_command = 'mv %s %s_bak%s' % (upload_path+webapp_name, upload_path+webapp_name, time_now)
            insert_log(log, log_list, '%s :服务器将%s修改为%s_bak%s' % (ip, upload_path+webapp_name, upload_path+webapp_name, time_now))
            sshUtil.my_remote_execute(conn, mv_command)
            recover_command = 'mv %s %s' % (upload_path+web, upload_path+webapp_name)
            insert_log(log, log_list, '%s :服务器将%s修改成%s' % (ip, upload_path+web, upload_path+webapp_name))
            sshUtil.my_remote_execute(conn, recover_command)

        else:
            insert_log(log, log_list, '%s :服务器%s' % (ip, '获取备份文件失败!,无法进行webapps还原操作！'))


def check_console_other(log, log_list, work, ip, port, conn):
    time.sleep(10)
    insert_log(log, log_list, '查看%s %s的控制台是否启动。。。' % (ip, port))
    insert_log(log, log_list, '服务器: %s检测过程持续5分钟,请耐心等待！！！' % ip)
    time_count = 1
    # couldn't connect to host
    while True:
        command2 = "curl http://%s:%s/console" % (ip, port)
        resulta = sshUtil.remote_excu3(conn, command2)
        # resulta = sshUtil.my_remote_execute(conn, command2)
        if 'console' in resulta:
            insert_log(log, log_list, '%s:%s:服务器启动成功！' % (ip, port))
            break
        time.sleep(2)
        time_count += 1
        if time_count == 150:
            insert_log(log, log_list, '%s: %s weblogic启动超过5分钟启动超时！-_-|||请检查原因！' % (ip, port))
            insert_log(log, log_list, resulta)
            conn.close()
            # raise RuntimeError('13')

def log_failed():
    """
    db2连接失败的地区
    """
    log_list = []
    ip = Application.objects.get(id=2)
    conn = sshUtil.create_conn(ip.app_ip, ip.account, ip.password)
    log_path = '/usr/local/log_test/'
    find_command = 'cd /; find %s -name *.log' % log_path
    find_log = sshUtil.remote_excu(conn, find_command)
    for log in find_log.split('\n'):
        cat_command = 'cat %s' % log
        log_info = sshUtil.remote_excu(conn, cat_command)
        if 'secussfully' not in log_info:
            area = log[log.rfind('/') + 1:][:(log[log.rfind('/') + 1:].rfind('.'))]
            log_list.append(area)
    print(json.dumps(log_list), 'log_list')


def radar_demo():
    radar = Radar()
    # data1 = [[12, 0, 2, 18, 0, 1]]
    radar_data1 = [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]#降水量
    # schema = [
    #     ("执行成功", 20), ("执行失败", 5), ("执行异常", 5),
    #     ("回滚成功", 20), ("回滚失败", 5), ("执行中断", 5)
    # ]
    schema = [
        ("Jan", 5), ("Feb", 10), ("Mar", 10),
        ("Apr", 50), ("May", 50), ("Jun", 200),
        ("Jul", 200), ("Aug", 200), ("Sep", 50),
        ("Oct", 50), ("Nov", 10), ("Dec", 5)
    ]
    radar.add_schema(schema)
    radar.add("执行状态", radar_data1)
    radar.render("/aa.html")

def line_demo():
    """按时间统计不同任务状态的任务"""




if __name__ == '__main__':
    """遗留问题，回退按钮，日志不刷新。，回退成功后可以再次回退？？？？"""
    # x = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # app = Application.objects.get(id=2)
    # ip = app.app_ip
    # port = app.port
    # conn = sshUtil.create_conn(ip, app.account, app.password)
    # command2 = "curl http://%s:%s/console" % (ip, port)
    # print(command2, 'com2')
    # resulta = sshUtil.remote_excu3(conn, command2)
    # print(resulta, 'aaaaa')
    # log_failed()
    # work = Work.objects.get(id=602)
    # success_count = 3
    # if success_count == 3:
    #     work.extend3 = str(work.extend3) + str(success_count)
    # # work.save(update_fields=['extend3'])
    # print(work.extend3, 'eee')
    # count = 0
    # list = [i for i in range(3)]
    # for i in str(work.extend3[4:]):
    #     if int(3) == int(i):
    #         count += 1
    # print(count)
    # if list.__len__() == count:
    #     print('yes')
    # else:
    #     print('no')

    # count_list = []
    # success_count = Work.objects.filter(work_status='执行成功').count()
    # failed_count = Work.objects.filter(work_status='执行失败').count()
    # exception_count = Work.objects.filter(work_status='执行异常').count()
    # rollback_success_count = Work.objects.filter(work_status='回退成功').count()
    # rollback_failed_count = Work.objects.filter(work_status='回退失败').count()
    # cut_count = Work.objects.filter(work_status='执行中断').count()
    # print(success_count, failed_count, exception_count, rollback_success_count, rollback_failed_count,cut_count)
    # count_list.append(success_count)
    # count_list.append(failed_count)
    # count_list.append(rollback_failed_count)
    # count_list.append(rollback_success_count)
    # count_list.append(exception_count)
    # count_list.append(cut_count)
    # print(count_list)
    # columns = ['执行成功', '执行失败', '回滚失败', '回滚成功', '执行异常', '执行中断']
    # bar = Bar("亚太自动化任务状态统计")
    # # bar.add_xaxis(columns).add_yaxis("数量", count_list)
    # # bar.add("执行状态", columns)
    # bar.add("数量", columns, count_list)
    # bar.render()
    line_demo()
    pass