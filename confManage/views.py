# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, render, redirect
from confManage.models import *
from tool.data_tool import *
from tool.passwd_tool import AESCrypto
import json
import tool.constant as CONFIG
import logging
from tool.sshUtil import get_user_ip

QUERYSET_FIRST_ELEM = CONFIG.SystemConfigs.QUERYSET_FIRST_ELEM
PROJECT_TYPE = CONFIG.SystemConfigs.PROJECT_TYPE
TAG_APP = CONFIG.SystemConfigs.TAG_APP
TAG_DB = CONFIG.SystemConfigs.TAG_DB

log = logging.getLogger('autoops')
@login_required(login_url='/')
def configs(request):
    log.info(get_user_ip(request)+'进入配置模块')
    result_list = getPublicParameterKeyword(keyword=PROJECT_TYPE)
    return render(request, 'config/configs.html', {"data": result_list})

@login_required(login_url='/')
def index(request):
    from work.views import get_project
    data = get_project(request)
    return render(request, 'index.html', {'data' : data})


@login_required(login_url='/')
def configsMsg(request):
    item_id = int(request.GET.get('thisItemId'))
    param = PublicParameter.objects.get(id=item_id)
    app_hosts = initHostInfoList(param.confV)
    platform,province,project = [],[],[]
    if len(app_hosts) != 0:
        platform = app_hosts[QUERYSET_FIRST_ELEM]['platform']
        province = app_hosts[QUERYSET_FIRST_ELEM]['province']
        project = app_hosts[QUERYSET_FIRST_ELEM]['project']
    data = {'platform': [],'province': [],'project': [],TAG_APP: [],TAG_DB: []}
    data = {
        'platform': platform,
        'province': province,
        'project': project,
        TAG_APP: app_hosts,
        TAG_DB: initDBInfoList(param.confV)
    }
    return render(request, 'config/configsMsg.html', {'data': data})


# 初始化主机信息的列表
def initHostInfoList(project):
    hosts = queryset_transducer(HostInfo.objects.filter(project=project, server_type=TAG_APP).values())
    for host in hosts:
        host['app_info'] = getProjectInfoKeyword(host['id'])
    return hosts


# 根据关键字查询项目信息
def getProjectInfoKeyword(host_id):
    app = queryset_transducer(ProjectInfo.objects.filter(host_ip=host_id).values())[QUERYSET_FIRST_ELEM]
    return app


# 初始化数据库信息的列表
def initDBInfoList(project):
    db_hosts = queryset_transducer(HostInfo.objects.filter(project=project, server_type=TAG_DB).values())
    for host in db_hosts:
        host['db_info'] = getDBInfoKeyword(host['id'])
    return db_hosts


# 查询数据库信息
def getDBInfoKeyword(host_id):
    db = queryset_transducer(DBInfo.objects.filter(host_ip=host_id).values())[QUERYSET_FIRST_ELEM]
    return db


@login_required(login_url='/')
def createOrUpdateItem(request):
    item_id = int(request.GET.get('thisItemId'))
    data = {}
    if item_id != -1:
        data = PublicParameter.objects.get(id=item_id)
    return render(request, 'config/createOrUpdateItem.html', {'project': data})

def get_config_locator():
    platform = PublicParameter.objects.get(confK='platform')
    province = PublicParameter.objects.get(confK='province')
    projects = queryset_transducer(PublicParameter.objects.filter(confK='proj_type').values())
    return {
        'platforms': platform.confV.split(','),
        'provinces': province.confV.split(','),
        'projects': projects,
    }

@login_required(login_url='/')
def createOrUpdateAppServerConfig(request):
    cl = get_config_locator()
    middleware_type = PublicParameter.objects.get(confK='middleware_type')
    cl['middleware_type'] = middleware_type.confV.split(',')
    opt_type = request.GET.get('opt')
    if opt_type == 'u':
        cl['host'] = HostInfo.objects.get(id=request.GET.get('host_id'))
        cl['host'].password = AESCrypto.decrypt(AESCrypto.doing(cl['host'].password))
        cl['proj'] = ProjectInfo.objects.get(id=request.GET.get('content_id'))
        cl['proj'].middleware_pass = AESCrypto.decrypt(AESCrypto.doing(cl['proj'].middleware_pass))
    return render(request,'config/createOrUpdateAppServerConfig.html',cl)


@login_required(login_url='/')
def createOrUpdateDbServerConfig(request):
    cl = get_config_locator()
    opt_type = request.GET.get('opt')
    if opt_type == 'u':
        cl['host'] = HostInfo.objects.get(id=request.GET.get('host_id'))
        cl['host'].password = AESCrypto.decrypt(AESCrypto.doing(cl['host'].password))
        cl['db'] = DBInfo.objects.get(id=request.GET.get('content_id'))
        cl['db'].password = AESCrypto.decrypt(AESCrypto.doing(cl['db'].password))
    return render(request, 'config/createOrUpdateDbServerConfig.html', cl)


# 获得公共参数的列表
@login_required(login_url='/')
def getPublicParameterList(request):
    result_list = []
    result = PublicParameter.objects.all().values()
    for i in result:
        result_list.append(i)
    publicParameters = json.dumps({"data": result_list})
    return HttpResponse(publicParameters)


# 添加公共参数
@login_required(login_url='/')
def createOrUpdatePublicParameter(request):
    if request.method == 'POST':
        public_parameter = json.loads(request.POST.get('data'))
        if public_parameter['id'] != '':
            result = updatePublicParameter(public_parameter)
            return HttpResponse(result)

        if public_parameter['confI'] == '': public_parameter['confI'] = '什么也没有'
        PublicParameter.objects.create(confK=public_parameter['confK'], confV=public_parameter['confV'],
                                              confI=public_parameter['confI'])
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 通过confK GET 一个公共参数
def getPublicParameterKeyword(keyword):
    result_list = []
    result = PublicParameter.objects.filter(confK=keyword).values()
    for i in result:
        result_list.append(i)
    return result_list

# 通过 confK GET 一个公共参数 -- 请求获取
@login_required(login_url='/')
def getPublicParameterKeywordReq(request):

    return HttpResponse(queryset_transducer(PublicParameter.objects.filter(confK=request.POST.get('keyword')).values()))


# 更新公共参数信息
def updatePublicParameter(publicParameter):
    PublicParameter.objects.filter(id=publicParameter['id']) \
        .update(confV=publicParameter['confV'], confI=publicParameter['confI'])
    return 'success'


# 删除公共参数
@login_required(login_url='/')
def deletePublicParameter(request):
    if request.method == 'POST':
        id_list = request.POST.getlist('ids')
        for id in id_list:
            id = int(id)
            PublicParameter.objects.filter(id=id).delete()
        PublicParameter.objects.filter(id=id).delete()
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 添加主机信息
@login_required(login_url='/')
def createHostInfo(request):
    result = 'failed'
    if request.method == 'POST':
        hostInfo = {}
        for field in request.POST:
            hostInfo[field] = request.POST.get(field)
        hostInfo['password'] = str(AESCrypto.encrypt(hostInfo['password']))
        if hostInfo['id'] != '':
            result = updateHostInfo(hostInfo)
            return HttpResponse(result)
        chi = HostInfo.objects.create(IP=hostInfo['IP'], host_name=hostInfo['host_name'],
                                      server_type=hostInfo['server_type'],
                                      platform=hostInfo['platform'], province=hostInfo['province'],
                                      project=hostInfo['project'], account=hostInfo['account'],
                                      password=hostInfo['password'])
        if (chi != None):
            hostInfo['id'] = chi.id
            created = None
            if hostInfo['server_type'] == TAG_APP:
                created = createProjectInfo(hostInfo);
            else:
                created = createDBInfo(hostInfo);
            if (created != None):
                result = 'success'
    return HttpResponse(result)


# 根据IP查询主机信息
@login_required(login_url='/')
def getHostInfoKeyword(keyword):
    result_list = []
    result = HostInfo.objects.filter(IP=keyword).values()
    for i in result:
        result_list.append(i)
    return result_list

# 根据ID查询主机信息
def getHostInfoId(hid):
    return HostInfo.objects.get(id=hid)

# 更新主机信息
def updateHostInfo(hostInfo):
    result = 'failed'
    HostInfo.objects.filter(id=hostInfo['id']).update(IP=hostInfo['IP'], host_name=hostInfo['host_name'],
                                                      server_type=hostInfo['server_type'],
                                                      platform=hostInfo['platform'],
                                                      province=hostInfo['province'],
                                                      project=hostInfo['project'],
                                                      account=hostInfo['account'],
                                                      password=hostInfo['password'])
    updated = None
    if hostInfo['server_type'] == TAG_APP:
        updated = updateProjectInfo(hostInfo);
    else:
        updated = updateDBInfo(hostInfo);
    if (updated != None):
        result = 'success'
    return result


# 删除主机信息
@login_required(login_url='/')
def deleteHostInfo(request):
    id_list = request.POST.getlist('ids')
    for id in id_list:
        HostInfo.objects.filter(id=id).delete()
    return HttpResponse('success')


# 添加数据库信息
def createDBInfo(dbInfo):
    result = 'failed'
    dbInfo['db_password'] = str(AESCrypto.encrypt(dbInfo['db_password']))
    hostIp = HostInfo.objects.get(id=dbInfo['id'])
    di = DBInfo.objects.create(name=dbInfo['db_name'], account=dbInfo['db_account'], password=dbInfo['db_password'],
                               port=dbInfo['port'], tnsname=dbInfo['tnsname'], host_ip=hostIp)
    if di != None:
        result = 'success'
    return HttpResponse(result)


# 更新数据库信息
def updateDBInfo(dbInfo):
    host = HostInfo.objects.get(id=dbInfo['id'])
    DBInfo.objects.filter(id=dbInfo['content_id']).update(name=dbInfo['db_name'], account=dbInfo['db_account'],
                                                            password=str(AESCrypto.encrypt(dbInfo['db_password'])), port=dbInfo['port'],
                                                            tnsname=dbInfo['tnsname'], host_ip=host)
    return HttpResponse('success')


# 删除数据库信息
@login_required(login_url='/')
def deleteDBInfo(request):
    if request.method == 'Post':
        id_list = request.POST.getlist('ids')
        for id in id_list:
            DBInfo.objects.filter(id=id).delete()
        DBInfo.objects.filter(id=id).delete()
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 初始化项目的列表
@login_required(login_url='/')
def initProjectInfoList(request):
    result_list = []
    result_list.append(
        {'projectId': dict(json.loads(initDBInfoList(request)), **json.loads(initHostInfoList(request)))})
    data = json.dumps({'data': result_list})
    return HttpResponse(data)


# 添加项目的信息

def createProjectInfo(projectInfo):
    result = 'failed'
    projectInfo['middleware_pass'] = str(AESCrypto.encrypt(projectInfo['middleware_pass']))
    host = HostInfo.objects.get(id=projectInfo['id'])
    project_info = ProjectInfo.objects.create(app_directory=projectInfo['app_directory'],
                                              middleware_type=projectInfo['middleware_type'],
                                              cache_directory=projectInfo['cache_directory'],
                                              static_directory=projectInfo['static_directory'],
                                              middleware_name=projectInfo['middleware_name'],
                                              middleware_pass=projectInfo['middleware_pass'],
                                              url=projectInfo['url'],
                                              restart_script_path=projectInfo['restart_script_path'],
                                              host_ip=host)
    if project_info != None:
        result = 'success'
    return result


# 更新数据库信息
def updateProjectInfo(projectInfo):
    host = HostInfo.objects.get(id=projectInfo['id'])
    ProjectInfo.objects.filter(id=projectInfo['content_id']).update(app_directory=projectInfo['app_directory'],
                                                                    middleware_type=projectInfo['middleware_type'],
                                                                    cache_directory=projectInfo['cache_directory'],
                                                                    static_directory=projectInfo['static_directory'],
                                                                    middleware_name=projectInfo['middleware_name'],
                                                                    middleware_pass=str(AESCrypto.encrypt(projectInfo['middleware_pass'])),
                                                                    url=projectInfo['url'],
                                                                    restart_script_path=projectInfo[
                                                                        'restart_script_path'],
                                                                    host_ip=host)
    return HttpResponse('success')


# 删除项目信息
@login_required(login_url='/')
def deleteProjectInfo(request):
    if request.method == 'Post':
        id_list = request.POST.getlist('ids')
        for id in id_list:
            ProjectInfo.objects.filter(id=id).delete()
        ProjectInfo.objects.filter(id=id).delete()
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 通过项目id查询主机信息和数据库信息
@login_required(login_url='/')
def getHostInfoAndDbInfo(request):
    result_list = []
    list_dbInfo = []
    if request.method == 'POST':
        projectId = request.POST['id']
        list = ProjectInfo.objects.filter(id=projectId).select_related()
        list_host = [{"IP": i.host_ip.IP, "host_name": i.host_ip.host_name, "server_type": i.host_ip.server_type,
                      "platform": i.host_ip.platform, "province": i.host_ip.province, "project": i.host_ip.project,
                      "account": i.host_ip.account, "password": i.host_ip.password} for i in list]
        for i in list:
            dbinfo = i.host_ip.dbinfo_set.all().values()
            for i in dbinfo:
                list_dbInfo.append(i)
        result_list.append({'projectId': {'hostInfo': list_host, 'dbInfo': list_dbInfo}})
        data = json.dumps({'data': result_list})
    return HttpResponse(data)


# 通过三大参数查询主机信息
@login_required(login_url='/')
def get_host_by_three(request):
    return HttpResponse(queryset_transducer(HostInfo.objects.filter(
        platform=request.POST.get('platform'),
        province=request.POST.get('province'),
        project=request.POST.get('project')
    ).values('id','IP','server_type')).__str__())

# HTTP ERROR 400
def error_400(request):
    return render(request, 'error/400.html')

# HTTP ERROR 401
def error_401(request):
    return render(request, 'error/401.html')

# HTTP ERROR 403
def error_403(request):
    return render(request, 'error/403.html')

# HTTP ERROR 404
def error_404(request):
    return render(request, 'error/404.html')

# HTTP ERROR 405
def error_405(request):
    return render(request, 'error/405.html')

# HTTP ERROR 500
def error_500(request):
    return render(request, 'error/500.html')

# HTTP ERROR 500
def error_503(request):
    return render(request, 'error/503.html')