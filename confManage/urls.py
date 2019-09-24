from django.conf.urls import url,include
from .views import *

urlpatterns = [
    url(r'configs/', configs, name='configs'),
    url(r'getPublicParameterKeyword/', getPublicParameterKeyword, name='getPublicParameterKeyword'),
    url(r'getPublicParameterKeywordReq/', getPublicParameterKeywordReq, name='getPublicParameterKeywordReq'),
    url(r'createOrUpdateItem/', createOrUpdateItem, name='createOrUpdateItem'),
    url(r'createOrUpdatePublicParameter/', createOrUpdatePublicParameter, name='createOrUpdatePublicParameter'),
    url(r'deletePublicParameter/', deletePublicParameter, name='deletePublicParameter'),
    url(r'createOrUpdateAppServerConfig/', createOrUpdateAppServerConfig, name='createOrUpdateAppServerConfig'),
    url(r'createOrUpdateDbServerConfig/', createOrUpdateDbServerConfig, name='createOrUpdateDbServerConfig'),
    url(r'getHostInfoId/', getHostInfoId, name='getHostInfoId'),
    url(r'createHostInfo/', createHostInfo, name='createHostInfo'),
    url(r'deleteHostInfo/', deleteHostInfo, name='deleteHostInfo'),
    url(r'configsMsg/', configsMsg, name='configsMsg'),
    url(r'get_host_by_three/', get_host_by_three, name='get_host_by_three'),
]