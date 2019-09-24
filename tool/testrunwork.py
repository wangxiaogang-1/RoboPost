from tool.sshUtil import *
import logging


#定义日志打印
log = logging.getLogger('autoops')
#定义测试的所有参数
database_ip = '172.16.36.66'
database_machine_user = 'root'
database_machine_pwd = '123456'
database_name = 'orcl'
database_user = 'orcl'
database_pwd = 'orcl'
tns_name = 'orcl'
app_machine_ip = '172.16.36.66'
app_machine_user = 'root'
app_machine_pwd = '123456'
app_application_dir = '/home/weblogic/applications/circauto'
app_html_dir = '/home/weblogic/html'
app_application_bakdir = '/home/weblogic/applications_bak'
app_html_bakdir = '/home/weblogic/html_bak'
app_cache_dir = '/home/weblogic/appcache'
app_restart_dir_name = '/home/weblogic/restart.sh'
url = 'www.baidu.com'
local_public_dir = 'D:\\python\\'
remote_pulbic_dir = '/home/uploadtest/'
file_zip_names = 'CIITCBJAUTO_V3.01.622.zip,CIITCBJAUTO_V3.01.623.zip'


def runwork():
    #1.1首先连接数据库服务器，进行上传zip包
    file_zip_list = file_zip_names.split(',')   #获取多个zip包列表
    endinfo = 'echo $?'  #定义命令执行是否成功，”0“为成功，”1“为失败
    db_conn = create_conn(database_ip, database_machine_user, database_machine_pwd)
    for i in file_zip_list:
        sourcefile = joinfile(local_public_dir, i)
        targetfile = joinfile(remote_pulbic_dir,i)
        print(remote_upload(db_conn, sourcefile, targetfile))
        #1.2解压上传的zip压缩包
        command_unip = 'cd ' + remote_pulbic_dir + ';' + 'unzip -q -o ' + i + ';' + endinfo
        print(remote_excu(db_conn, command_unip))

        #1.3依次执行数据库sh脚本
        command_rundb = 'cd ' + targetfile[0:-4] + ';' + 'sh upgrade_life_db.sh' \
                        + ' ' + database_user + ' ' + database_pwd + ' ' + database_name + ';' + endinfo
        print(remote_excu(db_conn, command_rundb))
    db_conn.close()

    # 2.1依次串行连接应用服务器，进行上传zip包
    app_ip_list = app_machine_ip.split(',')   #获取多个应用ip列表
    for j in app_ip_list:
        app_conn = create_conn(j, app_machine_user, app_machine_pwd)
        for z in file_zip_list:
            sourcefile = joinfile(local_public_dir, z)
            targetfile = joinfile(remote_pulbic_dir, z)
            print(remote_upload(app_conn, sourcefile, targetfile))

            # 2.2依次解压上传的zip压缩包
            command_unip = 'cd ' + remote_pulbic_dir + ';' + 'unzip -q -o ' + z + ';' + endinfo
            print(remote_excu(app_conn, command_unip))

            #2.3依次备份源文件
            osname = 'OS_NAME=`uname`;'
            #依次备份应用文件
            command_app_bak = 'cd ' + app_application_bakdir + ';' + osname + 'if [ ${OS_NAME} = "AIX" ];then jar cf ' + app_application_dir.split('/')[-1] \
                          + '_`date +%Y%m%d%H%M`.jar ' + app_application_dir + ';else tar zcf ' + app_application_dir.split('/')[-1] \
                          + '_`date +%Y%m%d%H%M`.tgz ' + app_application_dir + '; fi;' + endinfo
            print(remote_excu(app_conn, command_app_bak))
            #依次备份静态文件
            command_html_bak = 'cd ' + app_html_bakdir + ';' + osname + 'if [ ${OS_NAME} = "AIX" ];then jar cf ' \
                               + 'html_`date +%Y%m%d%H%M`.jar ' + app_html_dir + ';else tar zcf ' \
                               + 'html_`date +%Y%m%d%H%M`.tgz ' + app_html_dir + '; fi;' + endinfo
            print(remote_excu(app_conn, command_html_bak))

            #2.4依次覆盖升级文件
            command_cover = 'cd ' + targetfile[0:-4] + ';' + 'cp -rf applications/' + app_application_dir.split('/')[-1] \
                                + '/* ' + app_application_dir + ';' + endinfo
            print(remote_excu(app_conn, command_cover))

        #2.5清除缓存文件
        command_cache = 'rm -rf ' + app_cache_dir + '/*;' + endinfo
        print(remote_excu(app_conn, command_cache))

        #2.6执行重启应用脚本
        command_restart = 'sh ' + app_restart_dir_name + ';' + endinfo
        print(remote_excu(app_conn, command_restart))

        #2.7检测URL
        command_url = 'curl -v ' + url
        print(remote_excu(app_conn, command_url))
        app_conn.close()
if __name__ == '__main__':
    runwork()