from django.conf.urls import url, include
from django.contrib import admin
from confManage import urls as conf
from confManage.views import *
from scriptManage import urls as script
from authManage import urls as auth
from work import urls as work
from django.views.static import serve
from environment import urls as envir
from django.conf import settings

urlpatterns = [
    url(r'^$', auth.login_page),
    url(r'^admin/', admin.site.urls),
    url(r'^index/', envir.index, name='index'),
    url(r'^auth/', include(auth)),
    url(r'^conf/', include(conf)),
    url(r'^script/', include(script)),
    url(r'^work/', include(work)),
    url(r'^environment/', include(envir)),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]

