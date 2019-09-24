from django.conf.urls import url,include
from .views import *

urlpatterns = [
    # test
    url(r'^test_all/', test_all, name='test_all'),
    url(r'^show_templates', show_templates, name='show_templates'),
    url(r'^show_servers_env', show_servers_env, name='show_servers_env'),
    url(r'^get_servers_account', get_servers_account, name='get_servers_account'),
    url(r'^init_work', init_work,  name='init_work'),
    url(r'^create_work$', create_work, name='create_work'),
    url(r'^edit_work', edit_work, name='edit_work'),
    url(r'^init_ips', init_ips, name='init_ips'),
    url(r'^run_work$', run_work, name='run_work'),
    # url(r'^get_log', get_log, name='get_log'),
    url(r'^create_work_util$', create_work_util, name='create_work_util'),
    url(r'^roll_back_view', roll_back_view, name='roll_back_view'),
    # config urls
    url(r'^configs/', configs, name='configs'),
    url(r'^createConfigPage/', create_config, name='createConfigPage'),
    url(r'^copy_temp_v/', copy_temp_v, name='copy_temp_v'),
    url(r'^createConfig/', createConfig, name='createConfig'),
    url(r'^cou_appserver_config/', cou_appserver_config, name='cou_appserver_config'),
    url(r'^del_temp/', del_temp, name='del_temp'),
    url(r'^del_app/', del_app, name='del_app'),
    url(r'^get_taserver/', get_taserver, name='get_taserver'),
    url(r'^create_temp_view/', create_temp_view, name='create_temp_view'),
    # issue urls
    url(r'^issue/', issue, name='issue'),
    url(r'^issue_data/', issue_data, name='issue_data'),
    url(r'^issue_time_data/', issue_time_data, name='issue_time_data'),
    url(r'^get30dayline/', get30dayline, name='get30dayline'),
    url(r'^get30dateline/', get30dateline, name='get30dateline'),
    url(r'^create_issue/', create_issue, name='create_issue'),
    url(r'^get_tempips/', get_tempips, name='get_tempips'),
    url(r'^get_params/', get_params, name='get_params'),
    url(r'^upload_zip/', upload_zip, name='upload_zip_env'),
    url(r'^update_issue/', update_issue, name='update_issue'),
    url(r'^del_work/', del_work, name='del_work'),
    url(r'^view_work_env/', view_work, name='view_work_env'),
    url(r'^create_work_util/', create_work_util, name='create_work_util'),
    url(r'^run_issue/', run_issue, name='run_issue'),
    url(r'^check_run/', check_run, name='check_run'),
    url(r'^kill_issue/', kill_issue, name='kill_issue'),
    url(r'^roll_back_view/', roll_back_view, name='roll_back_view'),
    url(r'^view_log/', trans_log, name='view_log'),

]
