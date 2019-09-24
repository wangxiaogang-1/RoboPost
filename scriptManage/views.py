from django.shortcuts import render, HttpResponse
from scriptManage.models import *
import os
import time
import json
# Create your views here.
import logging
from tool.file_tool import *
from tool.sshUtil import get_user_ip
import chardet
from tool.passwd_tool import AESCrypto
import chardet

log = logging.getLogger('autoops')


def test(request):
    Script.objects.all()
    return render(request, 'scripts/test.html')


def scripts(request):
    log.info(get_user_ip(request) + '进入脚本模块')
    return render(request, 'script/scripts.html')


def mods(request):
    log.info(get_user_ip(request) + '进入模板模块')
    return render(request, 'mod/mods.html')


def create_script(request):
    """
    创建脚本，下面的字段需要部分修改，和前台传递过来的数值保持一致
    :param request:
    :return:
    """

    if request.method == 'POST':
        # 可以获取上传文件的文件名
        tool_file = request.FILES.get('file')
        # 指定临时文件写入路径
        file_path = 'static/files/'
        # 这里写入文件后一定要关闭，要不然下面会读取不到
        f = open(os.path.join(file_path, tool_file.name), 'wb')
        for chunk in tool_file.chunks(chunk_size=1024):
            f.write(chunk)
        f.close()
        # 这里需要空字符的配合才能展示读取文件的内容
        data = ""
        # 第一遍读取获得脚本内容
        with open(os.path.join(file_path, tool_file.name), 'rt', encoding="UTF-8") as ff:
            data += ff.read()
        # 第二遍读取获得参数列表
        with open(os.path.join(file_path, tool_file.name), 'rt', encoding="UTF-8") as ff:
            content = ff.readlines()
        params = get_parameter(content)
        # 注意，这里缺少（表名.字段名）信息，日后调整
        param_list = []
        for p_ke, p_val in params.items():
            for field, note in p_val.items():
                little_list = [field, note]
                param_list.append(little_list)
        # 转换一下可以存入数据库的格式，方便日后取出。
        pp = json.dumps(param_list, ensure_ascii=False)
        # 这里有一处给前台页面反馈信息，防止出现问题
        if param_list.__len__() == 0:
            result = '脚本文件参数格式不符合要求！'
            return HttpResponse(result)
        # 这里的编码是否要写到上面，反馈到前台，并提示脚本编码不一致的问题
        # 传递后删除，不占用存储信息
        os.remove(os.path.join(file_path, tool_file.name))

        if request.method == 'POST':
            script = {}
            for field in request.POST:
                script[field] = request.POST.get(field)
            Script.objects.create(function_name='测试脚本', script_info=data, script_code='utf-8',
                                  script_type='was', script_language='python', param_list=pp,
                                  author='leon', upload_time=int(time.time()), file_name=tool_file)
            result = 'success'
        else:
            result = 'failed'

        return HttpResponse(result)


# 初始化脚本
def init_script(request):
    """
    查询所有脚本内容展示到前台，考虑要不要吧分页传到tool中
    :param request:
    :return:
    """
    s = Script.objects.all().values()
    # 这个就是要传到前台列表格式的
    all_scripts = list(s)
    # print(all_scripts)
    for script in all_scripts:
        print(script)
    return HttpResponse('init_script')


# 删除脚本


def delete_script(request):
    """
    删除脚本，传递脚本，列表，多个或者一个都可以进行删除
    :param request:
    :return:
    """
    if request.method == 'POST':
        # 是不是getlist可以直接获取str的列表并进行转换？
        id_list = request.POST.getlist('ids')
        for id in id_list:
            Script.objects.filter(id=id).delete()
        res = 'success'
    else:
        res = 'failed'
    return HttpResponse(res)


# 更新脚本
def update_script(request):
    """
    待改动，部分数据需要转换格式进行存储，先看看前台传来的内容是什么样的
    :param request:
    :return:
    """
    if request.method == 'POST':
        script = {}
        for field in request.POST:
            script[field] = request.POST.get(field)
        Script.objects.filter(id=script['id']).update(function_name=script['function_name'],
                                                      script_info=script['script_info'],
                                                      script_code=script['script_code'],
                                                      script_type=script['script_type'],
                                                      script_language=script['script_language'],
                                                      param_list=script['param_list'],
                                                      author=script['author'], upload_time=int(time.time()),
                                                      file_name=script['file_name'])
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 获得模板的列表
def getTempletList(request):
    result_list = []
    result = Templet.objects.all().values()
    for i in result:
        result_list.append(i)
    templetList = json.dumps({"templet": result_list})
    return HttpResponse(templetList)


# 添加模板
def createTemplet(request):
    if request.method == 'POST':
        templet = {}
        for field in request.POST:
            templet[field] = request.POST.get(field)
        Templet.objects.get_or_create(tem_name=templet['tem_name'],
                                      order_list=templet['order_list'],
                                      templet_type=templet['templet_type'],
                                      tem_introduce=templet['tem_introduce'],
                                      author=templet['author'],
                                      create_time=templet['create_time'])
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 查询模板
def getTempletKeyword(request):
    result_list = []
    if request.method == 'POST':
        keyword = request.POST['keyword']
        result = Templet.objects.filter(tem_name=keyword).values()
        for i in result:
            result_list.append(i)
        templetList = json.dumps({"data": result_list, "keyword": keyword})
    return HttpResponse(templetList)


# 更新模板
def updateTemplet(request):
    if request.method == 'POST':
        templet = {}
        for field in request.POST:
            templet[field] = request.POST.get(field)
        Templet.objects.filter(id=templet['id']).update(tem_name=templet['tem_name'],
                                                        order_list=templet['order_list'],
                                                        templet_type=templet['templet_type'],
                                                        tem_introduce=templet['tem_introduce'],
                                                        author=templet['author'],
                                                        create_time=templet['create_time'])
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 删除模板

def deleteTemplet(request):
    if request.method == 'Post':
        id_list = request.POST.getlist('ids')
        for id in id_list:
            Templet.objects.filter(id=id).delete()
        Templet.objects.filter(id=id).delete()
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)
