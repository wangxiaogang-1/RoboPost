from django.conf.urls import url,include
from .views import *

urlpatterns = [
    url(r'^mods/', mods, name='mods'),
    url(r'^scripts/', scripts, name='scripts'),
]