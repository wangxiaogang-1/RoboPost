# !usr/bin/python
# coding:utf-8
# Create your views here.
import logging
from tool import sshUtil
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect
from authManage import service

log = logging.getLogger('autoops')


# 登录页
def login_page(request):
    return render(request, 'login.html', status=200)


# 登入方法
def auth_login(request):
    log.info(sshUtil.get_user_ip(request)+"登录系统！")
    return HttpResponse(service.auth_login(request))


# 注销
@login_required(login_url='/')
def auth_logout(request):
    log.info(sshUtil.get_user_ip(request) + "登出系统！")
    logout(request)
    return redirect("/")


@login_required(login_url='/')
def userGroupList(request):
    log.info(sshUtil.get_user_ip(request) + "进入用户组模块！")
    userGroupList = service.getUserGroupList(request)
    return render(request, 'userGroup/userGroupList.html', {"data": userGroupList})


@login_required(login_url='/')
def addUserToUserGroup(request):
    return HttpResponse(service.addUserToUserGroup(request))


@login_required(login_url='/')
def createUserGroup(request):
    return HttpResponse(service.createUserGroup(request))


@login_required(login_url='/')
def updateUserGroup(request):
    return HttpResponse(service.updateUserGroup(request))


@login_required(login_url='/')
def deleteUserGroup(request):
    return HttpResponse(service.deleteUserGroup(request))


@login_required(login_url='/')
def initUserList(request):
    return HttpResponse(service.initUserList(request))


@login_required(login_url='/')
def userList(request):
    userList = service.getUsers(request)
    log.info(sshUtil.get_user_ip(request) + "进入用户模块！")
    return render(request, 'user/userList.html', {"users": userList})


@login_required(login_url='/')
def createOrUpdateUserPage(request):
    init_data = service.initCreateOrUpdateUser(request)
    return render(request, 'user/createOrUpdateUser.html', {"init_data": init_data})


@login_required(login_url='/')
def changePassword(request):
    return HttpResponse(service.changePassword(request));


@login_required(login_url='/')
def createOrUpdateUser(request):
    return HttpResponse(service.createOrUpdateUser(request));


@login_required(login_url='/')
def initUser(request):
    return HttpResponse(service.getUserByIdForInitUpdate(request));


@login_required(login_url='/')
def deleteUser(request):
    return HttpResponse(service.deleteUser(request));


@login_required(login_url='/')
def permissionList(request):
    result = service.permissionList(request)
    log.info(sshUtil.get_user_ip(request) + "进入权限模块！")
    return render(request, 'authority/authorityList.html', {"data": result})


@login_required(login_url='/')
def getUsersAndUsersGroupsInPermission(request):
    data = service.getUsersAndUsersGroupsInPermission(request)
    return HttpResponse(data.__str__())


@login_required(login_url='/')
def updateUsersAndUsersGroupsInPermission(request):
    result = service.updateUsersAndUsersGroupsInPermission(request)
    return HttpResponse(result)


@login_required(login_url='/')
def getGroupPermission(request):
    result = service.getGroupPermission(request)
    return HttpResponse(result)


@login_required(login_url='/')
def getUserPermission(request):
    result = service.getUserPermission(request)
    return HttpResponse(result)


@login_required(login_url='/')
def savePermissionToGroupOrUser(request):
    result = service.savePermissionToGroupOrUser(request)
    return HttpResponse(result)
