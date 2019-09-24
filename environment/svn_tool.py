# coding:utf-8
from django.test import TestCase

import os
import sys
from datetime import datetime
from environment.util import *
from subprocess import Popen, PIPE
from environment.test import *

def svn_update(local_svn, local_public_dir, work, log, log_list):
    jkd1_6 = "export JAVA_HOME=/home/wlgma/install_package/java/jdk1.6.0_45"
    # 执行svn命令
    svn_command = 'svn update %s' % local_svn
    obj = Popen(svn_command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
    obj.wait()
    svn_readlines = obj.stdout.readlines()
    insert_log(log, log_list, '1.开始获取svn更新信息:')

    for read in svn_readlines:
        insert_log(log, log_list, bytes.decode(read))
    error = obj.stderr.read()
    # 如果svn执行命令有误将报错。
    if error.__len__() != 0:
        insert_log(log, log_list, bytes.decode(error))
        raise RuntimeError('7')
    # 设置svn更新的列表
    change_list = []
    # change_list.append('webapps/template/apitemplate/prpall/business/PersonalShortTermLoanPolicy.mrf\n')
    # 将修改或添加的新文件路径写入文件
    for line in svn_readlines:
        if b'invoker-client.xml' in line:
            pass
        elif b'A    ' in line:
            # 这里需要对byte类型进行转换
            change_list.append(bytes.decode(line))
        elif b'U    ' in line:
            change_list.append(bytes.decode(line))
        elif b'G    ' in line:
            change_list.append(bytes.decode(line))
    # 循环jar包加入build.xml
    for jar in svn_readlines:
        if b'.jar' in jar:
            update_build(local_svn+'build.xml', bytes.decode(jar))
    # 这里考虑什么时候删除文件，可以发布成功之后再删除文件!
    # 每次重新写入文件
    if change_list.__len__() == 0:
        # 判断work_status
        judge_status(work.id)
        # svn更新内容为空，证明没有代码被提交！
        # 需要提前判断jar包的源文件文件是否存在。
        exist = os.path.exists(local_svn + '/' + get_value(work.id, 'target_file_name'))
        if exist is True:
            # 判断work_status
            judge_status(work.id)
            file_read = open(local_svn + '/' + get_value(work.id, 'target_file_name'), 'r')
            read = file_read.readlines()
            # 如果存了，并且文件中写有内容
            if read.__len__() != 0:
                # 判断work_status
                judge_status(work.id)
                # 列标中有需要打包的内容
                ant_delete = 'cd ' + local_svn + '; ' + jkd1_6 + '; ant clean'
                insert_log(log, log_list, '清空classes文件')
                ant_de = Popen(ant_delete, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True,close_fds=True)
                ant_de.wait()
                if 'BUILD SUCCESSFUL' in bytes.decode(ant_de.stdout.read()):
                    insert_log(log, log_list, 'ant delete 清除文件成功')
                elif 'BUILD FAILED' in bytes.decode(ant_de.stdout.read()):
                    insert_log(log, log_list, 'ant delete 清除文件失败')
                ant_command = 'cd ' + local_svn + '; ' + jkd1_6 + '; ant'
                insert_log(log, log_list, '打包之前的svn内容')
                insert_log(log, log_list, 'ant 编译文件开始')
                insert_log(log, log_list, '该过程花费1-3分钟，请耐心等待。。。')
                ant = Popen(ant_command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
                ant.wait()
                ant_info = bytes.decode(ant.stdout.read())
                insert_log(log, log_list, ant_info)
                if "BUILD SUCCESSFUL" in ant_info:
                    # 判断work_status
                    judge_status(work.id)
                    insert_log(log, log_list, '文件编译成功')
                    # 文件编译成功后将编译好的文件根据更新列表进行打包
                    file = make_jar(local_svn, local_public_dir, work, log, log_list, 1)
                    return file
                else:
                    # 如果有错报出相关异常信息
                    raise RuntimeError('2')
            else:
                raise RuntimeError('1')
        else:
            raise RuntimeError('1')
    else:
        # 如果有内容，则将内容进行过滤处理
        # 判断work_status
        judge_status(work.id)
        f = open(local_svn + '/' + get_value(work.id, 'target_file_name'), 'a')
        target_len = f.readlines().__len__()
        for i in change_list:
            content = i[5:]
            # 这个目录应该配置入库
            pj_class = get_value(work.id, 'pj_class_dir')
            pj_key_word = get_value(work.id, 'pj_key_work')
            webapps_name = get_value(work.id, 'webapp_name')
            # 如果更新的是java文件
            rest_content = content[content.find(pj_key_word):][pj_key_word.__len__():]
            if '.java' in i:
                he = pj_class + rest_content.replace('java', 'class').replace('\\', '/')
                f.writelines(he)
            # 如果更新的是其他的文件
            elif webapps_name in i:
                he = i[i.find(webapps_name):]
                f.writelines(he)
            else:
                he = pj_class + rest_content.replace('\\', '/')
                f.writelines(he)
        f.close()
        # 判断work_status
    judge_status(work.id)
    # 列标中有需要打包的内容
    ant_delete = 'cd ' + local_svn + '; ' + jkd1_6 + '; ant clean'
    insert_log(log, log_list, '清空classes文件')
    ant_de = Popen(ant_delete, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
    ant_de.wait()
    if 'BUILD SUCCESSFUL' in bytes.decode(ant_de.stdout.read()):
        insert_log(log, log_list, 'ant delete 清除文件成功')
    elif 'BUILD FAILED' in bytes.decode(ant_de.stdout.read()):
        insert_log(log, log_list, 'ant delete 清除文件失败')
    ant_command = 'cd ' + local_svn + '; ' + jkd1_6 + '; ant'
    insert_log(log, log_list, '打包更新svn内容')
    insert_log(log, log_list, 'ant 编译文件开始')
    insert_log(log, log_list, '该过程花费1-3分钟，请耐心等待。。。')
    ant = Popen(ant_command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
    ant.wait()
    ant_info = bytes.decode(ant.stdout.read())
    insert_log(log, log_list, ant_info)
    if "BUILD SUCCESSFUL" in ant_info:
        # 判断work_status
        judge_status(work.id)
        insert_log(log, log_list, '文件编译成功')
        # 文件编译成功后将编译好的文件根据更新列表进行打包
        file = make_jar(local_svn, local_public_dir, work, log, log_list, target_len)
        return file
    else:
        raise RuntimeError('2')


# 如果编译成功后，我们需要打包操作！
def make_jar(local_svn, local_public_dir, work, log, log_list, target_len):
    base_encode(local_svn, work, log, log_list, target_len)
    # 执行windows上的命令进行打包操作
    now = get_YMD()
    # pa = sys.path[0]
    # 这里是否需要根据系统进行判断
    # pa.rfind('\\')
    # 这个webapps是否需要进行存库
    # 以及打包文件的名称
    time_jar = get_value(work.id, 'webapp_name') + now + ".jar"
    jar_command = "cd " + local_svn + "; jar -cvf " + time_jar + " @" + get_value(work.id, 'target_file_name')
    jar_status = Popen(jar_command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
    jar_status.wait()
    ant_error = jar_status.stderr.readlines()
    insert_log(log, log_list, bytes.decode(jar_status.stdout.read(), encoding='utf-8'))
    if ant_error.__len__() == 0:
        # 判断work_status
        judge_status(work.id)
        insert_log(log, log_list, '生成jar包成功')
        # 如果打包成功开始移动文件
        move_command = "cd " + local_svn + "; mv " + time_jar + " " + local_public_dir
        # remove = os.system(move_command)
        remove = Popen(move_command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
        if remove.stderr.read().__len__() == 0:
            # 判断work_status
            judge_status(work.id)
            insert_log(log, log_list, '准备将jar包上传至目标机器')
            return time_jar
        else:
            raise RuntimeError('5')
    else:
        raise RuntimeError('6')


def svn_log(filepath):
    command = 'svn log %s -r 6660:6665' % filepath
    x = os.popen(command)


def base_encode(local_svn, work, log, log_list, target_len):
    # 1.删除classes下的文件夹
    # rm_classes = 'rm -rf %s' % local_svn + judge_path(get_value(work.id, 'pj_class_dir')) + 'resources/'
    rm_classes = 'cd %s;rm -rf *' % (local_svn + judge_path(get_value(work.id, 'pj_class_dir')) + 'resources/')
    print(rm_classes)
    objj = Popen(rm_classes, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
    objj.wait()
    # 2.上来首先就应该添加那些编码的文件了
    try:
        name, other_list = language_encode(judge_path(get_value(work.id, 'local_svn')))
        insert_log(log, log_list, '语言文件转换')
    except Exception as e:
        raise e
    # 3.执行生成的文件
    excute_file = 'cd %s ; sh %s' % (local_svn + '/component/resources/', name)
    excute_obj = Popen(excute_file, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True, close_fds=True)
    excute_obj.wait()
    # 将语言文件写入打包内容
    if target_len == 0 :
        f = open(local_svn + '/' + get_value(work.id, 'target_file_name'), 'a')
        f.writelines(other_list)
        insert_log(log, log_list, '编码文件写入targetlist文件')


def get_YMD():
    now = datetime.now().strftime('%m%d%H%M')
    return now


def language_encode(project_path):
    # /home/wlgma/install_package/test_evn/component/resources

    f = open(project_path + '/component/resources/ApplicationResources.cmd')
    contents = f.readlines()
    new_list = []
    print('before')
    for content in contents:
        if 'del /F' in content:
            pass
        elif 'pause' in content:
            pass
        else:
            new_list.append(content.replace('\\', '/').replace('native2ascii', 'native2ascii -encoding gbk'))
    print('end')
    ff = open(project_path + '/component/resources/ApplicationResources.sh', 'w')
    ff.writelines(new_list)
    f.close()
    ff.close()
    other_list=[]
    for aa in new_list:
        if 'webapps' in aa:
            other_list.append(aa[aa.find('webapps'):].replace('\\', '/'))

    return 'ApplicationResources.sh', other_list


if __name__ == '__main__':
    f = open(r'C:\Users\Leon\Desktop\ApplicationResources.cmd')
    contents = f.readlines()
    new_list = []
    for content in contents:
        if 'del /F' in content:
            pass
        elif 'pause' in content:
            pass
        else:
            new_list.append(content)
    ff = open(r'C:\Users\Leon\Desktop\ApplicationResources.sh', 'w')
    ff.writelines(new_list)
    f.close()
    ff.close()
    other_list=[]
    for aa in new_list:
        if 'webapps' in aa:
            other_list.append(aa[aa.find('webapps'):].replace('\\', '/'))
