from django.conf.urls import url,include
from .views import *

urlpatterns = [
    url(r'^works/', works, name='works'),
    url(r'^createOrUpdateWorkPage/', createOrUpdateWorkPage, name='createOrUpdateWorkPage'),
    url(r'^selectPackage/', selectPackage, name='selectPackage'),
    url(r'^createOrUpdateWork/', createOrUpdateWork, name='createOrUpdateWork'),
    url(r'^initUpdateWork/', initUpdateWork, name='initUpdateWork'),
    url(r'^delete_work/', delete_work, name='delete_work'),
    url(r'^run_work/', run_work, name='run_work'),
    url(r'^run_work_single/', run_work_single, name='run_work_single'),
    url(r'^show_work/', show_work, name='show_work'),
    url(r'^stop_work/', stop_work, name='stop_work'),
    url(r'^get_log/', send_log, name='get_log'),
    url(r'^upload/', upload, name='upload'),
    url(r'^upload_mutifile/', upload_mutifile, name='upload_mutifile'),
    url(r'^upload_zip/', upload_zip, name='upload_zip'),
]