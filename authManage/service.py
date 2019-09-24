import json
from authManage.models import *
from confManage.models import PublicParameter
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group, User, Permission
from django.db.models import Q
from django.shortcuts import HttpResponse
from tool.data_tool import *
import tool.constant as CONFIG

QUERYSET_FIRST_ELEM = CONFIG.SystemConfigs.QUERYSET_FIRST_ELEM

truth_table = {
    'status': {
        True: 1,
        False: 0
    }
}

# 获取用户组列表
def getUserGroupList(request):
    return Group.objects.all().values()

# 初始化新增/更新用户数据
def initCreateOrUpdateUser(request):
    opt = request.GET.get('opt')
    init_data = {}
    init_data['groups'] = Group.objects.all().values().order_by('id')
    user_iden = PublicParameter.objects.get(confK='user_iden')
    init_data['user_iden'] = user_iden.confV.split(',')
    user_status = PublicParameter.objects.get(confK='user_status')
    init_data['user_status'] = user_status.confV.split(',')
    init_data['user_groups'] = []
    init_data['user'] = {}
    if opt == 'u':
        user = User.objects.get(id=request.GET.get('uid'))
        init_data['user_groups'] = user.groups.all().values().order_by('id')
        init_data['user'] = User.objects.filter(id=request.GET.get('uid')).values()[QUERYSET_FIRST_ELEM]
    return init_data


# 通过用户ID获得group的列表
def getUserGroupListByUserId(request):
    result_list = []
    groups = Group.objects.filter(user__id=request.POST.get('userId')).values_list('id').order_by('id')
    for i in groups:
        result_list.append(i)
    return result_list


# 添加组
def createUserGroup(request):
    if request.method == 'POST':
        name = request.POST['name']
        if len(Group.objects.filter(name=name)) > 0:
            result = 'exist'
        else:
            Group.objects.create(name=name)
            result = 'success'
    else:
        result = 'failed'
    return result


# 查询组信息
def getUserGroupsByKeyword(request):
    result_list = []
    if request.method == 'POST':
        keyword = request.POST['keyword']
        result = Group.objects.filter(name__contains=keyword).values_list('id', 'name')
        for i in result:
            result_list.append(i)
        result_list = queryset_transducer(result_list)
        new_dict = {}
        for i in result_list:
            new_dict[i[QUERYSET_FIRST_ELEM]] = i[1]
        userGroupList = json.dumps({"data": new_dict, "keyword": keyword})
    return HttpResponse(userGroupList)


# 更新组信息
def updateUserGroup(request):
    if request.method == 'POST':
        id = request.POST['id']
        name = request.POST['name']
        Group.objects.filter(id=id).update(name=name)
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 删除组
def deleteUserGroup(request):
    if request.method == 'POST':
        id_list = request.POST.getlist('ids')
        for ugid in id_list:
            group = Group.objects.filter(id=int(ugid)).delete()
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 初始化用户数据列表
def initUserList(request):
    result_list = []
    users = User.objects.all().values('id', 'username', 'first_name', 'last_name', 'is_superuser')
    for i in users:
        result_list.append(i)
    g_users = getUsersByUserGroupId(request)
    for ul in result_list:
        for gul in g_users:
            if (ul['id'] == gul['id']):
                ul['statusClass'] = True
    userList = json.dumps({"users": result_list})
    return HttpResponse(userList)


# 组成员管理
def addUserToUserGroup(request):
    result = 'success'
    if request.method == 'POST':
        userGroupId = request.POST['userGroupId']
        userid_list = json.loads(request.POST.get('userIds'))
        group = Group.objects.get(id=userGroupId)
        group.user_set.clear()
        for userid in userid_list:
            group.user_set.add(User.objects.get(id=int(userid)))
    else:
        result = 'failed'
    return HttpResponse(result)


# 获得用户的列表
def getUsers(request):
    result_list = []
    users = User.objects.all().values('id', 'username', 'first_name', 'last_name', 'last_login', 'date_joined',
                                      'is_superuser', 'is_active')
    for i in users:
        result_list.append(i)
    return result_list


# 通过用户组ID获获取用户列表
def getUsersByUserGroupId(request):
    result_list = []
    ugid = request.POST.get('userGroupId')
    users = User.objects.filter(groups__id=ugid).values('id', 'first_name', 'last_name', 'username')
    for i in users:
        result_list.append(i)
    return result_list


# 通过用户组ID获获取用户列表
def getUserByIdForInitUpdate(request):
    result_list = []
    uid = int(request.POST.get('userId'))
    user = User.objects.filter(id=uid).values()
    groupsInUser = queryset_transducer(Group.objects.filter(user__id=uid).values_list('id'))
    for i in user:
        result_list.append(i)
    user = result_list[QUERYSET_FIRST_ELEM]
    del user['password'], user['date_joined'], user['last_login'], user['is_staff']
    user['is_active'] = truth_table['status'][user['is_active']]
    user['is_superuser'] = truth_table['status'][user['is_superuser']]
    user['groupsInUser'] = groupsInUser.__str__()
    return user.__str__()


# 修改用户密码
def changePassword(request):
    uid = request.POST.get('userId')
    newPasswd = request.POST.get('newPasswd')
    user = User.objects.get(id=uid)
    user.set_password(newPasswd)
    user.save()
    return 'success';


# 查询用户信息
def getUsersByKeyword(request):
    result_list = []
    if request.method == 'POST':
        keyword = request.POST['keyword']
        result = User.objects.filter(name__contains=keyword).values_list('id', 'username')
        for i in result:
            result_list.append(i)
        result_list = queryset_transducer(result_list)
        new_dict = {}
        for i in result_list:
            new_dict[i[QUERYSET_FIRST_ELEM]] = i[1]
        userList = json.dumps({"data": new_dict, "keyword": keyword})
    return HttpResponse(userList)


# 初始化组数据列表
def initGroupList(request):
    result_list = []
    groups = Group.objects.all().values('id', 'name')
    for i in groups:
        result_list.append(i)
    data = {"userGroups": result_list}
    userList = json.dumps(data)
    return userList


# 更新用户信息
def createOrUpdateUser(request):
    if request.method == 'POST':
        user = json.loads(request.POST.get('data'))
        if (int(user['id']) != -1):
            result = updateUser(request)
            return HttpResponse(result)
        user['userGroupIds'] = json.loads(user['userGroupIds'])
        if len(User.objects.filter(username=user['username'])) > 0:
            return HttpResponse('exist')
        else:
            user_created = User(username=user['username'], is_superuser=user['is_superuser'],
                                first_name=user['first_name'], last_name=user['last_name'], email=user['email'],
                                is_staff=user['is_staff'],
                                is_active=user['is_active'])
            user_created.set_password(user['password'])
            user_created.save()
            if (len(user['userGroupIds']) != 0):
                for groupid in user['userGroupIds']:
                    user_created.groups.add(Group.objects.get(id=int(groupid)))
            result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 添加新用户
def updateUser(request):
    result = 'failed'
    if request.method == 'POST':
        user = json.loads(request.POST.get('data'))
        user['userGroupIds'] = json.loads(user['userGroupIds'])
        user_updated = User.objects.filter(id=user['id'])
        result = user_updated.update(username=user['username'], is_superuser=user['is_superuser'],
                            first_name=user['first_name'], last_name=user['last_name'], email=user['email'],
                            is_active=user['is_active'])
        u = User.objects.get(id=user['id'])
        if result != 0:
            result = 'success'
        u.groups.clear()
        if (len(user['userGroupIds']) != 0):
            for groupid in user['userGroupIds']:
                u.groups.add(Group.objects.get(id=int(groupid)))
    return result


# 删除请求的用户
def deleteUser(request):
    if request.method == 'POST':
        id_list = request.POST.getlist('ids')
        for id in id_list:
            User.objects.filter(id=int(id)).delete()
        User.objects.filter(id=int(id)).delete()
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 获取所有权限
def permissionList(request):
    result_list = []
    permissions = Permission.objects.all().values('id', 'name')
    for i in permissions:
        result_list.append(i)
    uig = getUsersInnerGroups(request)
    return {"permission": result_list, "uag": uig}


# 获取所有组和组中所有用户
def getUsersInnerGroups(request):
    result = {
        'userInGroup' : [],
        'userNotInGroup' : []
    }
    groups = Group.objects.all().values('id', 'name')
    all_user = User.objects.filter(groups=None).values('id', 'first_name', 'last_name', 'username')
    for user in all_user:
        result['userNotInGroup'].append(user)
    for group in groups:
        userInGroup = User.objects.filter(groups__id=group['id']).values('id', 'first_name', 'last_name', 'username')
        group['users'] = []
        for i in userInGroup:
            group['users'].append(i)
        grop = Group.objects.get(id=group['id'])
        if (len(grop.user_set.all()) != 0):
            result['userInGroup'].append(group)
    return result


# 查找权限信息
def getPermissionByKeyword(request):
    result_list = []
    if request.method == 'POST':
        keyword = request.POST['keyword']
        result = Permission.objects.filter(name__contains=keyword).values_list('id', 'name')
        for i in result:
            result_list.append(i)
        result_list = queryset_transducer(result_list)
        new_dict = {}
        for i in result_list:
            new_dict[i[QUERYSET_FIRST_ELEM]] = i[1]
        permissionList = json.dumps({"data": new_dict, "keyword": keyword})
    return HttpResponse(permissionList)


# 初始化所有权限a
def initPermission(request):
    result_list = []
    result_list.append({'permissionId': dict(json.loads(initGroupList(request)), **json.loads(initUserList(request)))})
    data = json.dumps({'data': result_list})
    return HttpResponse(data)


# 获取所有拥有该权限的组和用户
def getUsersAndUsersGroupsInPermission(request):
    result_list, result_list2, result_list3 = [], [], []
    if request.method == 'POST':
        permissionId = int(request.POST['permissionId'])
        groups = Group.objects.filter(Q(permissions__id=permissionId)).values_list('id').distinct()
        for group in groups:
            result_list.append(group[QUERYSET_FIRST_ELEM])
        users = User.objects.filter(Q(user_permissions=permissionId)).values_list('id').distinct()
        for user in users:
            result_list2.append(user[QUERYSET_FIRST_ELEM])
        data = {'permissionId': permissionId, 'usersGroup': result_list, 'users': result_list2}
    return data


# 更新请求的权限关联的所有用组和用户
def updateUsersAndUsersGroupsInPermission(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        permissionId = int(data['permissionId'])
        permission = Permission.objects.get(id=permissionId)
        permission.user_set.clear()
        permission.group_set.clear()
        userGroups = data['userGroups']
        users = data['users']
        for gid in userGroups:
            ug = Group.objects.get(id=int(gid))
            permission.group_set.add(ug)
        for uid in users:
            user = User.objects.get(id=int(uid))
            permission.user_set.add(user)
        result = 'success'
    else:
        result = 'failed'
    return HttpResponse(result)


# 获取组拥有的全部权限
def getGroupPermission(request):
    groupId = int(request.POST.get('groupId'))
    group = Group.objects.get(id=groupId)
    permissions = group.permissions.all().values_list('id')
    result = []
    for p in permissions:
        result.append(p[QUERYSET_FIRST_ELEM])
    return result.__str__()


# 获取用户拥有的全部权限
def getUserPermission(request):
    userId = int(request.POST.get('userId'))
    user = User.objects.get(id=userId)
    permissions = Permission.objects.filter(user__id=userId).values_list('id')
    result = []
    for p in permissions:
        result.append(p[QUERYSET_FIRST_ELEM])
    return result.__str__()


# 为组批量添加权限
def savePermissionToGroup(request):
    data = json.loads(request.POST.get('data'))
    groupId = int(data['groupId'])
    group = Group.objects.get(id=groupId)
    permissionIds = data['permissions']
    group.permissions.clear()
    for pid in permissionIds:
        permission = Permission.objects.get(id=int(pid))
        group.permissions.add(permission)
    return 'success'


# 为用户批量添加权限
def savePermissionToUser(request):
    data = json.loads(request.POST.get('data'))
    userId = int(data['userId'])
    user = User.objects.get(id=userId)
    permissionIds = data['permissions']
    user.user_permissions.clear()
    for pid in permissionIds:
        permission = Permission.objects.get(id=int(pid))
        user.user_permissions.add(permission)
    return 'success'


# 为组和用户批量添加权限
def savePermissionToGroupOrUser(request):
    data = json.loads(request.POST.get('data'))
    groupId = int(data['groupId'])
    userId = int(data['userId'])
    result = 'failed'
    if (groupId == -1):
        result = savePermissionToUser(request)
    elif (userId == -1):
        result = savePermissionToGroup(request)
    return result


# 登录
def auth_login(request):
    result = 'success:'
    username = request.POST.get('username')
    passwd = request.POST.get('passwd')
    user = authenticate(username=username, password=passwd)
    if user:
        user_msg = {}
        user_p = User.objects.filter(username=username).values('id', 'username', 'first_name', 'last_name', 'is_superuser',
                                                      'is_active', 'email')[QUERYSET_FIRST_ELEM]
        user_group = list(Group.objects.filter(user=user).values('name'))
        for key in user_p:
            user_msg[key] = user_p[key]
        modules = getUserModules(user_msg)
        if len(modules) == 0:
            return HttpResponse('error:null_permission_error') # 用户权限为空异常
        else:
            result += modules[QUERYSET_FIRST_ELEM]['url']
        login(request, user)
        functions = getUserFunction(user_msg)
        request.session['modules'] = modules
        request.session['user'] = user_msg
        request.session['functions'] = functions
        request.session['groups'] = user_group
    else:
        result = 'error:uname_or_passwd_error'
    return HttpResponse(result)


# 获取用户有可用的模块权限
def getUserModules(login_user):
    user = User.objects.get(id=login_user['id'])
    all_permission = Permission.objects.filter(content_type__model='module').order_by('id').values()
    modules = []
    for permission in all_permission:
        if user.has_perm('authManage.' + permission['codename']):
            q_module = queryset_transducer(Module.objects.filter(codename=permission['codename']).values())
            modules.append(q_module[QUERYSET_FIRST_ELEM])
    return modules


# 获取用户可用的功能权限
def getUserFunction(login_user):
    user = User.objects.get(id=login_user['id'])
    functions = []
    all_permission = Permission.objects.filter(content_type__model='function').values();
    for permission in all_permission:
        if user.has_perm('module.' + permission['codename']):
            q_function = Function.objects.filter(content_type__model='function', codename=permission['codename']).values_list()
            for f_field in q_function:
                functions.append(f_field)
    return functions
