"""
@author  :jie.xu
@file    : sshUtil.py
@time    : 2018/3/8 15:44
"""
import paramiko
import os
import chardet


# 创建远程链接方法
def create_conn(host, user, passwd, port=22):
    s = paramiko.SSHClient()  #
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts文件中的主机。
    s.connect(hostname=host, port=port, username=user, password=passwd)
    return s


def my_remote_execute(conn, command):
    _, stdout, stderr = conn.exec_command("source /etc/profile;source ~/.bashrc;" + command)
    b_out, b_err = stdout.read(), stderr.read()
    s_out = b_out.decode(chardet.detect(b_out).get('encoding')) if b_out else ''
    s_err = b_err.decode(chardet.detect(b_err).get('encoding')) if b_err else ''
    if s_err:
        return s_err.strip()
    return s_out.strip()


# 远程上传文件方法
def remote_upload(conn, sourceFile, targetFile):
    sftp = conn.open_sftp()
    sftp.put(sourceFile, targetFile)


# 远程执行命令方法
def remote_excu(conn, command):
    # stdin, stdout, stderr = conn.exec_command("source /etc/profile;source ~/.bashrc;"+command)
    stdin, stdout, stderr = conn.exec_command(command)
    stdin.write("Y")  # 一般来说，第一个连接，需要一个简单的交互
    result1 = stderr.read().decode(encoding='gbk', errors='ignore')
    result2 = stdout.read().decode(encoding='gbk', errors='ignore')
    if len(result1) < 1:
        result = result2.strip()
    else:
        result = result1.strip()
    return result


def remote_excu3(conn, command):
    stdin, stdout, stderr = conn.exec_command(command)
    stdin.write("Y")  # 一般来说，第一个连接，需要一个简单的交互
    result1 = stderr.read().decode('gbk')
    result2 = stdout.read().decode('gbk')
    return result2.strip()


# 拼接文件目录和文件名称
def joinfile(path, filename):
    name = os.path.join(path, filename)
    return name


# 定义linux路径专用拼接目录和文件
def joinlinux(path, filename):
    if path.split('/')[-1] == '':
        return path + filename
    else:
        return path + '/' + filename


# 返回用户跟IP的字符串，用于日志打印
def get_user_ip(request):
    if type(request) == list:
        user = request[0]
        userIP = request[1]
    else:
        user = request.user.username

        userIP = request.META.get("REMOTE_ADDR", None)
    return 'user"："%s","ip":"%s","message":"' % (user, userIP)
