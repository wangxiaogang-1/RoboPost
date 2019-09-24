from django.conf.urls import url,include
from .views import *

urlpatterns = [
    url(r'auth_login/$', auth_login, name='auth_login'),
    url(r'auth_logout/$', auth_logout, name='auth_logout'),
    url(r'userGroup/userGroupList/$', userGroupList, name='userGroupList'),
    url(r'userGroup/createUserGroup/$', createUserGroup, name='createUserGroup'),
    url(r'userGroup/addUserToUserGroup/$', addUserToUserGroup, name='addUserToUserGroup'),
    url(r'userGroup/updateUserGroup/$', updateUserGroup, name='updateUserGroup'),
    url(r'userGroup/deleteUserGroup/$', deleteUserGroup, name='deleteUserGroup'),
    url(r'userGroup/initUserList/$', initUserList, name='initUserList'),
    url(r'user/userList/$', userList, name='userList'),
    url(r'user/createOrUpdateUserPage/$', createOrUpdateUserPage, name='createOrUpdateUserPage'),
    url(r'user/createOrUpdateUser/$', createOrUpdateUser, name='createOrUpdateUser'),
    url(r'user/initUser/$', initUser, name='initUser'),
    url(r'user/changePassword/$', changePassword, name='changePassword'),
    url(r'user/deleteUser/$', deleteUser, name='deleteUser'),
    url(r'permission/permissionList/$', permissionList, name='permissionList'),
    url(r'permission/getUsersAndUsersGroupsInPermission/$', getUsersAndUsersGroupsInPermission, name='getUsersAndUsersGroupsInPermission'),
    url(r'permission/updateUsersAndUsersGroupsInPermission/$', updateUsersAndUsersGroupsInPermission, name='updateUsersAndUsersGroupsInPermission'),
    url(r'permission/getGroupPermission$', getGroupPermission, name='getGroupPermission'),
    url(r'permission/getUserPermission', getUserPermission, name='getUserPermission'),
    url(r'permission/savePermissionToGroupOrUser', savePermissionToGroupOrUser, name='savePermissionToGroupOrUser'),
]