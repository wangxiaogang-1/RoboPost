# coding:utf-8
config_dict = {
    '1': ['svn中没有可更新的文件', '无更新'],
    '2': ['javac编译失败，或程序没有安装ant工具,或本地svn路径有误！', '执行异常'],
    '3': ['由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败', '执行异常'],
    '4': ['jar包上传失败，请检查模板配置中的应用信息,查看上传路径的配置是否正确！', '执行异常'],
    '5': ['jar包移动失败，请检查本地jar包生成路径local_public_dir是否配置正确?', '执行异常'],
    '6': ['jar包生成失败，请检查本地项目路径local_svn是否配置正确\n'
          '或查看targetfile.txt文件中生成的路径是否存在问题', '执行异常'],
    '7': ['当前所配置的本地SVN路径local_svn地址有误\n'
          '或当前配置目录不属于svn文件，请检查路径是否有误\n'
          'svn: E155007: None of the targets are working copies', '执行异常'],
    '8': ['cp: 无法获取的文件状态(stat): 没有那个文件或目录,备份项目文件失败', '执行异常'],
    '9': ['文件解压失败！', '执行异常'],
    '10': ['没有查询到该端口号的pid，请检查应用配置中端口号是否填写正确\n'
           '或项目是否正在运行', '执行异常'],
    '11': ['终结进程失败，没有此进程或应用配置表中端口号填写有误', '执行异常'],
    '12': ['Weblogic停止失败，详情请查看上方日志！', '执行异常'],
    '13': ['Weblogic启动超时，详情请查看上方日志', '执行异常'],
    '14': ['执行被中断', '执行中断'],
    '15': ['没有相关机器的配置信息，请在模板的应用配置信息中进行配置', '执行异常'],
    '16': ['当前所配置的本地SVN路径local_svn地址有误\n'
           '或当前配置目录不属于svn文件，请检查路径是否有误\n', '执行异常'],

    '17': ['恢复webapps包失败', '执行异常'],
    '18': ['bin/stopWeblogic.sh脚本执行失败，导致服务器停止失败，请相关人员查询原因，项目包已进行备份操作', '回退成功'],
    '19': ['weblogic启动时间超时，请检查是否java代码有误，请相关人员查找原因，项目包已进行备份操作！', '回退成功'],
    }
PUBLIC_DIR = '/home/wlgma/install_package/RoboPost/public_dir/'
