from work.models import *
from tool.sshUtil import *
import logging
import tool.gol
import time
import json
from tool.passwd_tool import AESCrypto
import requests
import datetime


'''
描述执行状态码：
0 未执行
1 执行中
2 执行成功
3 执行中断
4 执行错误
'''

#初始化全局变量
tool.gol._init()
#定义日志打印
log = logging.getLogger('autoops')



#执行作业方法
def runwork(request, workid):
    # 定义日志表的日志数据格式
    log_total = {}
    workinfo = WorkInfo.objects.get(pk=workid)
    # listtest = [{"key":"database_ip","value":"172.16.36.66","info":"数据库IP"},{"key":"database_machine_user","value":"root","info":"数据库机器用户名"},{"key":"database_machine_pwd","value":"b'\\xec\\x99\\xd7\\xe7U\\x02\\x02eF\\xa2\\x93\\xfd\\xc0I\\x8e\\x9f'","info":"数据库机器密码"},{"key":"database_name","value":"orcl","info":"数据库名称"},{"key":"database_user","value":"orcl","info":"数据库用户名"},{"key":"database_pwd","value":"orcl","info":"数据库密码"},{"key":"tns_name","value":"orcl","info":"数据库tns"},{"key":"app_machine_ip","value":"172.16.36.66","info":"应用机器IP"},{"key":"app_machine_user","value":"root","info":"应用机器用户名"},{"key":"app_machine_pwd","value":"b'\\xec\\x99\\xd7\\xe7U\\x02\\x02eF\\xa2\\x93\\xfd\\xc0I\\x8e\\x9f'","info":"应用机器密码"},{"key":"app_application_dir","value":"/home/weblogic/applications/circauto","info":"应用程序目录"},{"key":"app_html_dir","value":"/home/weblogic/html","info":"应用静态目录"},{"key":"app_application_bakdir","value":"/home/weblogic/applications_bak","info":"应用备份目录"},{"key":"app_html_bakdir","value":"/home/weblogic/html_bak","info":"静态备份目录"},{"key":"app_cache_dir","value":"/home/weblogic/appcache","info":"应用缓存目录"},{"key":"app_restart_dir_name","value":"/home/weblogic/restart.sh","info":"应用重启脚本目录"},{"key":"url","value":"http://www.baidu.com","info":"应用url"},{"key":"local_public_dir","value":"D:\\python\\","info":"本地公共目录"},{"key":"remote_app_pulbic_dir","value":"/home/uploadtest/","info":"app远程公共目录"},{"key":"remote_db_pulbic_dir","value":"/home/uploadtest/","info":"db远程公共目录"}]
    # workinfo.value_list = json.dumps(listtest, ensure_ascii=False)
    # workinfo.save()
    value_lists = json.loads(workinfo.value_list)
    '''
    将作业表里的参数列表值重组成需要的字典格式：
    将原有的格式如：[{'key': 'database_ip','value':'172.16.36.66','info':'数据库IP'},{'key': 'database_machine_user','value':'root','info':'数据库机器用户名'}]
    转变成：{'database_ip': '172.16.36.66', 'database_machine_user': 'root'}
    '''
    value_list = {}
    for item in value_lists:
        value_list[item['key']] = item['value']
    # 获取所有作业执行参数
    database_ip = value_list['database_ip']
    database_machine_user = value_list['database_machine_user']
    database_machine_pwd = value_list['database_machine_pwd']
    database_name = value_list['database_name']
    database_user = value_list['database_user']
    database_pwd = value_list['database_pwd']
    tns_name = value_list['tns_name']
    app_machine_ip = value_list['app_machine_ip']
    app_machine_user = value_list['app_machine_user']
    app_machine_pwd = value_list['app_machine_pwd']
    app_application_dir = value_list['app_application_dir']
    app_html_dir = value_list['app_html_dir']
    app_application_bakdir = value_list['app_application_bakdir']
    app_html_bakdir = value_list['app_html_bakdir']
    app_cache_dir = value_list['app_cache_dir']
    app_restart_dir_name = value_list['app_restart_dir_name']
    url = value_list['url']
    local_public_dir = value_list['local_public_dir']
    remote_app_pulbic_dir = value_list['remote_app_pulbic_dir']
    remote_db_pulbic_dir = value_list['remote_db_pulbic_dir']
    file_zip_names = workinfo.file_package_names

    #定义执行作业进度总步数
    step_all = len(file_zip_names.split(',')) + len(app_machine_ip.split(','))
    #定义执行作业计步器初始值（全局参数）
    tool.gol.set_value('count', 0)
    #定义日志格式：数据库和应用执行日志列表，此列表添加到全局变量里，最终更新到日志表里
    list_db = []
    list_app = []

    #如果作业状态是0：未开始，则进入执行作业方法，修改状态为1：执行中，修改开始时间，并保存
    if workinfo.work_status == 0:
        workinfo.work_status = 1
        workinfo.start_time = int(time.time())
        workinfo.save()
        #初始化作业日志
        worklog = WorkLog(work_id=workid, work_name=workinfo.work_name, log=json.dumps(log_total, ensure_ascii=False))
        worklog.save()
    log.info(get_user_ip(request) + "进入执行作业方法！%s执行中..." % (workinfo.work_name))
    worklog = WorkLog.objects.get(work_id=workid)
    flag = True
    while flag:
        if workinfo.work_status == 2 or workinfo.work_status == 4 or workinfo.work_status == 3:
            break
        #1.1首先连接数据库服务器，进行上传zip包
        file_zip_list = sorted(file_zip_names.split(','))   #获取多个zip包列表
        endinfo = 'echo $?'  #定义命令执行是否成功，”0“为成功，”1“为失败
        database_machine_pwd = AESCrypto.decrypt(AESCrypto.doing(database_machine_pwd))
        try:
            db_conn = create_conn(database_ip, database_machine_user, database_machine_pwd)
        except Exception as e:
            conn_error = "数据库服务器%s连接失败：" % (database_ip) + e.__str__()
            log.info(get_user_ip(request) + conn_error)
            insertlog(list_db, conn_error, workid, log_total, 'db:' + database_ip, worklog)
            workinfo.work_status = 4
            workinfo.end_time = int(time.time())
            workinfo.save()
            break

        conn_success = "数据库服务器%s连接成功....." % (database_ip)
        log.info(get_user_ip(request) + conn_success)
        # database_ip = 'jyf123.456'
        insertlog(list_db, conn_success, workid, log_total, 'db:' + database_ip, worklog)
        #循环zip包进行上传
        for i in range(len(file_zip_list)):
            sourcefile = joinfile(local_public_dir, file_zip_list[i])
            #创建以当前时间+zip包命名的文件夹名称
            time_zip_name = '.'.join([now_time_specify(), file_zip_list[i]])
            command_mkdir = 'cd ' + remote_db_pulbic_dir + ';' + 'mkdir ' + time_zip_name
            remote_excu(db_conn, command_mkdir)
            #拼接远程db公共目录和创建的新的文件夹名称
            remote_db_pulbic_dir_end = joinlinux(remote_db_pulbic_dir, time_zip_name)
            targetfile = joinlinux(remote_db_pulbic_dir_end, file_zip_list[i])
            db_upload_log = '数据库服务器%s操作:' % (database_ip) + ',开始上传:' + file_zip_list[i] + '升级包'
            # 更新作业日志（上传日志）
            insertlog(list_db, db_upload_log, workid, log_total, 'db:' + database_ip, worklog)
            log.info(get_user_ip(request) + db_upload_log)
            upload1 = remote_upload(db_conn, sourcefile, targetfile)
            if upload1 is not None:
                insertlog(list_db, upload1, workid, log_total, 'db:' + database_ip, worklog)
                upload1_error = '数据库服务器%s操作:' % (database_ip) + '上传升级包:' + file_zip_list[i] + '失败，执行错误...'
                log.info(get_user_ip(request) + upload1_error)
                insertlog(list_db, upload1_error, workid, log_total, 'db:' + database_ip, worklog)
                workinfo.work_status = 4
                workinfo.end_time = int(time.time())
                workinfo.save()
                flag = False
                break
            else:
                upload1_success = '数据库服务器%s操作:' % (database_ip) + '上传升级包:' + file_zip_list[i] + '成功...'
                log.info(get_user_ip(request) + upload1_success)
                insertlog(list_db, upload1_success, workid, log_total, 'db:' + database_ip, worklog)
            if workstop(workid) == 0:
                error_log = "执行被中断！！！............."
                insertlog(list_db, error_log, workid, log_total, 'db:' + database_ip, worklog)
                log.info(get_user_ip(request) + error_log)
                tool.gol.del_value(workid)
                flag = False
                break

            #1.2解压上传的zip压缩包
            db_unzip_log_start = '数据库服务器%s操作:' % (database_ip) + ',解压上传的zip升级包:' + file_zip_list[i]
            log.info(get_user_ip(request) + db_unzip_log_start)
            # 更新作业日志（开始解压zip日志）
            insertlog(list_db, db_unzip_log_start, workid, log_total, 'db:' + database_ip, worklog)
            command_unzip = 'cd ' +   + ';' + 'unzip -q -o ' + file_zip_list[i] + ';' + endinfo
            db_unzip_log = remote_excu(db_conn, command_unzip)

            if db_unzip_log[-1] != '0':
                # 更新作业日志（解压zip日志完成）
                insertlog(list_db, db_unzip_log, workid, log_total, 'db:' + database_ip, worklog)
                workinfo.work_status = 4
                workinfo.end_time = int(time.time())
                workinfo.save()
                error = '数据库服务器%s操作:' % (database_ip) + '升级包:' + file_zip_list[i] + '解压失败，执行错误...'
                insertlog(list_db, error, workid, log_total, 'db:' + database_ip, worklog)
                log.info(get_user_ip(request) + error)
                tool.gol.del_value(workid)
                flag = False
                break
            else:
                db_unzip_log_end = '数据库服务器%s操作:' % (database_ip) + '升级包:' + file_zip_list[i] + '解压成功...'
                insertlog(list_db, db_unzip_log_end, workid, log_total, 'db:' + database_ip, worklog)
                log.info(get_user_ip(request) + db_unzip_log_end)
            if workstop(workid) == 0:
                error_log = "执行被中断！！！............."
                insertlog(list_db, error_log, workid, log_total, 'db:' + database_ip, worklog)
                log.info(get_user_ip(request) + error_log)
                tool.gol.del_value(workid)
                flag = False
                break

            #1.3依次执行数据库sh脚本
            db_rundb_log_start = '数据库服务器%s操作:' % (database_ip) + ',开始执行数据库sh脚本:upgrade_life_db.sh：'
            log.info(get_user_ip(request) + db_rundb_log_start)
            #更新作业日志（开始执行数据库sh脚本日志）
            insertlog(list_db, db_rundb_log_start, workid, log_total, 'db:' + database_ip, worklog)
            database_pwds = AESCrypto.decrypt(AESCrypto.doing(database_pwd))
            command_rundb = 'source /etc/profile;source .bash_profile;cd ' + remote_db_pulbic_dir_end + ';' + 'sh upgrade_life_db.sh' \
                            + ' ' + database_user + ' ' + database_pwds + ' ' + database_name + ';' + endinfo
            db_rundb_log = remote_excu(db_conn, command_rundb)
            command_log = 'cd ' + remote_db_pulbic_dir_end + ';' + 'cat *upgrade_asp_db.log'
            db_rundb_log2 = remote_excu(db_conn, command_log)
            #更新作业执行进度
            tool.gol.set_value('count', i + 1)
            workinfo.run_status = int(tool.gol.get_value('count') * 100 / step_all)
            workinfo.save()
            if db_rundb_log[-1] != '0':
                # 更新作业日志（执行数据库sh脚本日志完成）
                insertlog(list_db, db_rundb_log, workid, log_total, 'db:' + database_ip, worklog)
                db_rundb_log2 = "以下是upgrade_asp_db.log即时日志：" + db_rundb_log2
                insertlog(list_db, db_rundb_log2, workid, log_total, 'db:' + database_ip, worklog)
                workinfo.work_status = 4
                workinfo.end_time = int(time.time())
                workinfo.save()
                error = '数据库服务器%s操作:' % (database_ip) + 'upgrade_life_db.sh脚本执行失败，执行错误...'
                insertlog(list_db, error, workid, log_total, 'db:' + database_ip, worklog)
                log.info(get_user_ip(request) + error)
                tool.gol.del_value(workid)
                tool.gol.del_value('count')
                flag = False
                break
            else:
                # 更新作业日志（执行数据库sh脚本日志完成）
                insertlog(list_db, db_rundb_log[0:-1], workid, log_total, 'db:' + database_ip, worklog)
                db_rundb_log2 = "以下是upgrade_asp_db.log即时日志：" + db_rundb_log2
                insertlog(list_db, db_rundb_log2, workid, log_total, 'db:' + database_ip, worklog)
                db_rundb_log_end = '数据库服务器%s操作:' % (database_ip) + 'upgrade_life_db.sh脚本本身执行成功，但脚本中重定向的sql是否执行成功请核查upgrade_asp_db.log即时日志...'
                log.info(get_user_ip(request) + db_rundb_log_end)
                insertlog(list_db, db_rundb_log_end, workid, log_total, 'db:' + database_ip, worklog)
            if workstop(workid) == 0:
                error_log = "执行被中断！！！............."
                log.info(get_user_ip(request) + error_log)
                insertlog(list_db, error_log, workid, log_total, 'db:' + database_ip, worklog)
                tool.gol.del_value(workid)
                tool.gol.del_value('count')
                flag = False
                break
        db_conn.close()
        tool.gol.del_value(workid)
        if not flag:
            break
        # 2.1依次串行连接应用服务器，进行上传zip包
        app_ip_list = app_machine_ip.split(',')   #获取多个应用ip列表
        app_user = app_machine_user.split(',')    #获取多个应用服务器用户名列表
        app_pwd = app_machine_pwd.split(',')      #获取多个应用服务器密码列表（加密状态）
        app_pwd_dec = [AESCrypto.decrypt(AESCrypto.doing(pwd)) for pwd in app_pwd]  #转换解密状态的密码列表
        for j in range(len(app_ip_list)):
            try:
                app_conn = create_conn(app_ip_list[j], app_user[j], app_pwd_dec[j])
            except Exception as e:
                conn_error = "应用服务器%s用户名或密码错误，连接失败：" % (app_ip_list[j]) + e.__str__()
                log.info(get_user_ip(request) + conn_error)
                insertlog(list_app, conn_error, workid, log_total, app_ip_list[j], worklog)
                workinfo.work_status = 4
                workinfo.end_time = int(time.time())
                workinfo.save()
                flag = False
                break

            conn_success = "应用服务器%s连接成功....." % (app_ip_list[j])
            log.info(get_user_ip(request) + conn_success)
            insertlog(list_app, conn_success, workid, log_total, app_ip_list[j], worklog)
            for z in range(len(file_zip_list)):
                sourcefile = joinfile(local_public_dir, file_zip_list[z])
                # 创建以当前时间+zip包命名的文件夹名称
                time_zip_name = '.'.join([now_time_specify(), file_zip_list[z]])
                command_mkdir = 'cd ' + remote_app_pulbic_dir + ';' + 'mkdir ' + time_zip_name
                remote_excu(app_conn, command_mkdir)
                # 拼接远程app公共目录和创建的新的文件夹名称
                remote_app_pulbic_dir_end = joinlinux(remote_app_pulbic_dir, time_zip_name)
                targetfile = joinlinux(remote_app_pulbic_dir_end, file_zip_list[z])
                app_upload_log = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始上传:' + file_zip_list[z] + '升级包'
                # 更新作业日志（上传日志）
                insertlog(list_app, app_upload_log, workid, log_total, app_ip_list[j], worklog)
                log.info(get_user_ip(request) + app_upload_log)
                upload2 = remote_upload(app_conn, sourcefile, targetfile)
                if upload2 is not None:
                    insertlog(list_app, upload2, workid, log_total, app_ip_list[j], worklog)
                    upload2_error = '应用服务器%s操作:' % (app_ip_list[j]) + '上传升级包:' + file_zip_list[z] + '失败，执行错误...'
                    log.info(get_user_ip(request) + upload2_error)
                    insertlog(list_app, upload2_error, workid, log_total, app_ip_list[j], worklog)
                    workinfo.work_status = 4
                    workinfo.end_time = int(time.time())
                    workinfo.save()
                    flag = False
                    break
                else:
                    upload2_success = '应用服务器%s操作:' % (app_ip_list[j]) + '上传升级包:' + file_zip_list[z] + '成功...'
                    log.info(get_user_ip(request) + upload2_success)
                    insertlog(list_app, upload2_success, workid, log_total, app_ip_list[j], worklog)
                if workstop(workid) == 0:
                    tool.gol.del_value(workid)
                    error_log = "执行被中断！！！............."
                    insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                    log.info(get_user_ip(request) + error_log)
                    flag = False
                    break

                # 2.2依次解压上传的zip压缩包
                app_unzip_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始解压:' + file_zip_list[z] + '升级包'
                # 更新作业日志（开始解压zip压缩包日志）
                insertlog(list_app, app_unzip_log_start, workid, log_total, app_ip_list[j], worklog)
                log.info(get_user_ip(request) + app_unzip_log_start)
                command_unip = 'cd ' + remote_app_pulbic_dir_end + ';' + 'unzip -q -o ' + file_zip_list[z] + ';' + endinfo
                app_unzip_log = remote_excu(app_conn, command_unip)

                if app_unzip_log != '0':
                    # 更新作业日志（解压zip压缩包日志完成）
                    insertlog(list_app, app_unzip_log, workid, log_total, app_ip_list[j], worklog)
                    workinfo.work_status = 4
                    workinfo.end_time = int(time.time())
                    workinfo.save()
                    error = '应用服务器%s操作:' % (app_ip_list[j]) + '升级包:' + file_zip_list[z] + '解压失败，执行错误...'
                    insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
                    log.info(get_user_ip(request) + error)
                    tool.gol.del_value(workid)
                    flag = False
                    break
                else:
                    app_unzip_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + '升级包:' + file_zip_list[z] + '解压成功...'
                    log.info(get_user_ip(request) + app_unzip_log_end)
                    insertlog(list_app, app_unzip_log_end, workid, log_total, app_ip_list[j], worklog)
                if workstop(workid) == 0:
                    error_log = "执行被中断！！！............."
                    log.info(get_user_ip(request) + error_log)
                    insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break

                #2.3依次备份源文件
                osname = 'OS_NAME=`uname`;'
                #依次备份应用文件
                app_bak_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始备份应用文件:'
                log.info(get_user_ip(request) + app_bak_log_start)
                #新作业日志（开始备份应用文件日志）
                insertlog(list_app, app_bak_log_start, workid, log_total, app_ip_list[j], worklog)
                #根据app目录截取应用名称name
                app_application_dir_end = app_application_dir.split(',')
                if app_application_dir_end[j].split('/')[-1] == '':
                    app_name = app_application_dir_end[j].split('/')[-2]
                else:
                    app_name = app_application_dir_end[j].split('/')[-1]
                app_application_bakdir_end = joinlinux(app_application_bakdir, time_zip_name)
                command_app_bak = 'cd ' + app_application_bakdir_end + ';' + osname + 'if [ ${OS_NAME} = "AIX" ];then jar cf ' + app_name \
                              + '_`date +%Y%m%d%H%M`.jar ' + app_application_dir_end[j] + ';else tar Pzcf ' + app_name \
                              + '_`date +%Y%m%d%H%M`.tgz ' + app_application_dir_end[j] + '; fi;' + endinfo
                app_bak_log = remote_excu(app_conn, command_app_bak)


                if app_bak_log[-1] != '0':
                    # 更新作业日志（备份应用文件日志完成）
                    insertlog(list_app, app_bak_log, workid, log_total, app_ip_list[j], worklog)
                    workinfo.work_status = 4
                    workinfo.end_time = int(time.time())
                    workinfo.save()
                    error = '应用服务器%s操作:' % (app_ip_list[j]) + ',备份应用文件失败，执行错误...'
                    log.info(get_user_ip(request) + error)
                    insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break
                else:
                    app_bak_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + ',备份应用文件成功...'
                    log.info(get_user_ip(request) + app_bak_log_end)
                    insertlog(list_app, app_bak_log_end, workid, log_total, app_ip_list[j], worklog)
                if workstop(workid) == 0:
                    error_log = "执行被中断！！！............."
                    log.info(get_user_ip(request) + error_log)
                    insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break
                #依次备份静态文件
                app_bakhtml_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始备份静态文件:'
                log.info(get_user_ip(request) + app_bakhtml_log_start)
                # 新作业日志（开始备份静态文件日志）
                insertlog(list_app, app_bakhtml_log_start, workid, log_total, app_ip_list[j], worklog)
                app_html_bakdir_end = joinlinux(app_html_bakdir, time_zip_name)
                app_html_dir_end = app_html_dir.split(',')
                command_html_bak = 'cd ' + app_html_bakdir_end + ';' + osname + 'if [ ${OS_NAME} = "AIX" ];then jar cf ' \
                                   + 'html_`date +%Y%m%d%H%M`.jar ' + app_html_dir_end[j] + ';else tar Pzcf ' \
                                   + 'html_`date +%Y%m%d%H%M`.tgz ' + app_html_dir_end[j] + '; fi;' + endinfo
                app_bakhtml_log = remote_excu(app_conn, command_html_bak)


                if app_bakhtml_log[-1] != '0':
                    # 更新作业日志（备份静态文件日志完成）
                    insertlog(list_app, app_bakhtml_log, workid, log_total, app_ip_list[j], worklog)
                    workinfo.work_status = 4
                    workinfo.end_time = int(time.time())
                    workinfo.save()
                    error = '应用服务器%s操作:' % (app_ip_list[j]) + ',备份静态文件失败，执行错误...'
                    log.info(get_user_ip(request) + error)
                    insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break
                else:
                    app_bakhtml_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + ',备份静态文件成功...'
                    log.info(get_user_ip(request) + app_bakhtml_log_end)
                    insertlog(list_app, app_bakhtml_log_end, workid, log_total, app_ip_list[j], worklog)
                if workstop(workid) == 0:
                    error_log = "执行被中断！！！............."
                    log.info(get_user_ip(request) + error_log)
                    insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break

                #2.4依次覆盖升级文件
                app_cover_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始覆盖升级文件:'
                log.info(get_user_ip(request) + app_cover_log_start)
                # 新作业日志（开始覆盖升级文件日志）
                insertlog(list_app, app_cover_log_start, workid, log_total, app_ip_list[j], worklog)
                command_cover = 'cd ' + remote_app_pulbic_dir_end + ';' + 'cp -rf applications/' + app_name \
                                    + '/* ' + app_application_dir_end[j] + ';' + endinfo
                app_cover_log = remote_excu(app_conn, command_cover)


                if app_cover_log[-1] != '0':
                    # 更新作业日志（覆盖升级文件日志完成）
                    insertlog(list_app, app_cover_log, workid, log_total, app_ip_list[j], worklog)
                    workinfo.work_status = 4
                    workinfo.end_time = int(time.time())
                    workinfo.save()
                    error = '应用服务器%s操作:' % (app_ip_list[j]) + ',覆盖升级文件失败，执行错误...'
                    log.info(get_user_ip(request) + error)
                    insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break
                else:
                    app_cover_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + ',覆盖升级文件成功...'
                    log.info(get_user_ip(request) + app_cover_log_end)
                    insertlog(list_app, app_cover_log_end, workid, log_total, app_ip_list[j], worklog)
                if workstop(workid) == 0:
                    error_log = "执行被中断！！！............."
                    log.info(get_user_ip(request) + error_log)
                    insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break

            if not flag:
                break
            # #2.5清除缓存文件
            # app_cache_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始清除缓存文件:'
            # log.info(get_user_ip(request) + app_cache_log_start)
            # # 新作业日志（开始清除缓存文件日志）
            # insertlog(list_app, app_cache_log_start, workid, log_total, app_ip_list[j], worklog)
            # app_cache_dir_start = app_cache_dir.split('@')
            # app_cache_dir_end = app_cache_dir_start[j].split(',')
            # for x in range(len(app_cache_dir_end)):
            #     app_cache_dir_end[x] = joinlinux(app_cache_dir_end[x], '*')
            #     command_cache = 'rm -rf ' + app_cache_dir_end[x] + ';' + endinfo
            #     app_cache_log = remote_excu(app_conn, command_cache)
            #
            #
            #     if app_cache_log[-1] != '0':
            #         # 更新作业日志（清除缓存文件日志完成）
            #         insertlog(list_app, app_cache_log, workid, log_total, app_ip_list[j], worklog)
            #         workinfo.work_status = 4
            #         workinfo.end_time = int(time.time())
            #         workinfo.save()
            #         error = '应用服务器%s操作:' % (app_ip_list[j]) + ',清除缓存文件失败，执行错误...'
            #         log.info(get_user_ip(request) + error)
            #         insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
            #         tool.gol.del_value(workid)
            #         flag = False
            #         break
            #     else:
            #         app_cache_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + ',清除缓存文件成功...'
            #         log.info(get_user_ip(request) + app_cache_log_end)
            #         insertlog(list_app, app_cache_log_end, workid, log_total, app_ip_list[j], worklog)
            #     if workstop(workid) == 0:
            #         error_log = "执行被中断！！！............."
            #         log.info(get_user_ip(request) + error_log)
            #         insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
            #         tool.gol.del_value(workid)
            #         flag = False
            #         break
            #2.6执行重启应用脚本
            app_restart_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始执行重启应用脚本:'
            log.info(get_user_ip(request) + app_restart_log_start)
            # 新作业日志（开始执行重启应用脚本）
            insertlog(list_app, app_restart_log_start, workid, log_total, app_ip_list[j], worklog)
            app_restart_dir_name_end = app_restart_dir_name.split(',')
            app_restart_sh = joinlinux(app_restart_dir_name_end[j], 'restart.sh')
            command_jurge_restart = 'if [  -f ' + app_restart_sh + ' ];then echo "0";else echo "1";fi'
            command_jurge_log = remote_excu(app_conn, command_jurge_restart)
            if command_jurge_log == '1':
                jurge_log = "未找到restart.sh脚本，请检查重启脚本路径是否正确，或者此次升级不执行重启动作!!!"
                log.info(get_user_ip(request) + jurge_log)
                insertlog(list_app, jurge_log, workid, log_total, app_ip_list[j], worklog)
            elif command_jurge_log == '0':
                command_restart = 'source /etc/profile;source .bash_profile;' + 'sh ' + app_restart_sh + ';' + endinfo
                app_restart_log = remote_excu(app_conn, command_restart)
                if app_restart_log[-1] != '0':
                    # 更新作业日志（执行重启应用脚本日志完成）
                    insertlog(list_app, app_restart_log, workid, log_total, app_ip_list[j], worklog)
                    workinfo.work_status = 4
                    workinfo.end_time = int(time.time())
                    workinfo.save()
                    error = '应用服务器%s操作:' % (app_ip_list[j]) + ',重启应用restart.sh脚本本身执行失败，执行错误...'
                    log.info(get_user_ip(request) + error)
                    insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break
                else:
                    server_out = joinlinux(app_restart_dir_name_end[j], 'server.out')
                    server_out_command = '/bin/sleep 2;a=`grep "RUNNING mode" ' + server_out + ' |wc -l`;b=`grep "ADMIN mode" ' + server_out \
                                         + ' |wc -l`;time=0;while [ $a -eq 0 -a $b -eq 0 ];do /bin/sleep 1;((time++));a=`grep "RUNNING mode" ' + server_out \
                                         + ' |wc -l`;b=`grep "ADMIN mode" ' + server_out + ' |wc -l`;if [ $time -eq 600 ];then echo "timeout";break;fi;done;if [ $a -eq 1 ];then echo "1";fi;if [ $b -eq 1 ];then echo "2";fi'
                    server_out_log = remote_excu(app_conn, server_out_command)
                    server_out_message = 'server.out未判断出日志内容...'
                    if server_out_log == '1':
                        server_out_message = '从server.out中判断出：<Server started in RUNNING mode>, Restart weblogic sucessfully.'
                    elif server_out_log == '2':
                        server_out_message = '从server.out中判断出：<Server started in ADMIN mode>, Restart weblogic failed.Please check it.'
                    elif server_out_log == 'timeout':
                        server_out_message = '扫描server.out超时10分钟...请登录服务器自行查看server.out并判断是否重启成功！！！'
                    # 更新作业日志（执行重启应用脚本日志完成）
                    insertlog(list_app, app_restart_log[0:-1], workid, log_total, app_ip_list[j], worklog)
                    app_restart_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + ',重启应用restart.sh脚本本身执行成功，但还需查看重定向的server.out日志...'
                    log.info(get_user_ip(request) + app_restart_log_end)
                    insertlog(list_app, app_restart_log_end, workid, log_total, app_ip_list[j], worklog)
                    server_out_message = "以下是从server.out提取并判断的结果：" + server_out_message
                    insertlog(list_app, server_out_message, workid, log_total, app_ip_list[j], worklog)
                if workstop(workid) == 0:
                    error_log = "执行被中断！！！............."
                    log.info(get_user_ip(request) + error_log)
                    insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                    tool.gol.del_value(workid)
                    flag = False
                    break
            #2.7检测URL
            app_url_log_start = '应用服务器%s操作:' % (app_ip_list[j]) + ',开始检测URL:'
            log.info(get_user_ip(request) + app_url_log_start)
            # 新作业日志（开始检测URL）
            insertlog(list_app, app_url_log_start, workid, log_total, app_ip_list[j], worklog)
            urls = url.split(',')
            # command_url = 'curl -I -m 10 -o /dev/null -s -w %{http_code}  ' + url[j]
            # '''
            # -I 仅测试HTTP头
            # -m 10 最多查询10s
            # -o /dev/null 屏蔽原有输出信息
            # -s silent
            # -w %{http_code} 控制额外输出
            # '''
            # app_url_log = remote_excu(app_conn, command_url)
            r = requests.get(urls[j], allow_redirects=False)
            app_url_log = r.status_code

            # 更新作业日志（执行检测url日志完成）
            insertlog(list_app, str(app_url_log), workid, log_total, app_ip_list[j], worklog)
            # 更新作业执行进度
            tool.gol.set_value('count', tool.gol.get_value('count') + 1)
            workinfo.run_status = int(tool.gol.get_value('count') * 100 / step_all)
            workinfo.save()
            if app_url_log != 200:
                workinfo.work_status = 4
                workinfo.end_time = int(time.time())
                workinfo.save()
                error = '应用服务器%s操作:' % (app_ip_list[j]) + 'url检测不是200，检测失败，执行错误...'
                log.info(get_user_ip(request) + error)
                insertlog(list_app, error, workid, log_total, app_ip_list[j], worklog)
                tool.gol.del_value(workid)
                tool.gol.del_value('count')
                flag = False
                break
            else:
                app_url_log_end = '应用服务器%s操作:' % (app_ip_list[j]) + 'url检测是200，检测成功...'
                log.info(get_user_ip(request) + app_url_log_end)
                insertlog(list_app, app_url_log_end, workid, log_total, app_ip_list[j], worklog)
            if workstop(workid) == 0:
                error_log = "执行被中断！！！............."
                log.info(get_user_ip(request) + error_log)
                insertlog(list_app, error_log, workid, log_total, app_ip_list[j], worklog)
                tool.gol.del_value(workid)
                tool.gol.del_value('count')
                flag = False
                break
            app_conn.close()
            tool.gol.del_value(workid)
        tool.gol.del_value('count')
        if not flag:
            break
        log_end = '作业至此执行成功，执行完成................'
        list_end = [log_end]
        log_total['成功标志'] = list_end
        worklog.log = json.dumps(log_total, ensure_ascii=False)
        worklog.save()
        log.info(get_user_ip(request) + log_end)
        workinfo.work_status = 2
        workinfo.end_time = int(time.time())
        workinfo.save()


#判断是否为执行中断方法
def workstop(workid):
    workinfo = WorkInfo.objects.get(pk=workid)
    if workinfo.work_status == 3:
        workinfo.end_time = int(time.time())
        workinfo.save()
        return 0


#实时插入作业日志方法
def insertlog(listlog, messages, workid, log_total, ip, worklog):
    listlog.append(messages)
    tool.gol.set_value(workid, listlog)
    log_total[ip] = tool.gol.get_value(workid)
    worklog.log = json.dumps(log_total, ensure_ascii=False)
    worklog.save()


#获取日志方法
def getlog(workid):
    workinfo = WorkInfo.objects.get(pk=workid)
    worklog = WorkLog.objects.get(work_id=workid)
    if workinfo.work_status == 0:
        info = '作业未开始执行！！！'
        return info
    else:
        return json.loads(worklog.log)


def now_time_specify():
    nowtime = datetime.datetime.now()
    list1 = str(nowtime).split(' ')
    list2 = list1[1].split('.')
    list2[0] = list2[0].replace(':', '-')
    list3 = [list1[0], list2[0]]
    result = '-'.join(list3)
    return result
