import json
import os, django
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RoboPost.settings")
# django.setup()
import pymysql
from environment.util import *
from RoboPost.settings import DATABASES


def create_and_run(work):
    db = pymysql.connect(host=DATABASES['default']['HOST'], port=int(DATABASES['default']['PORT']), user=DATABASES['default']['USER'],
                         passwd=DATABASES['default']['PASSWORD'], db=DATABASES['default']['NAME'])
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    select_work_sql = "select * from work where id=%s" % work.id
    cursor.execute(select_work_sql)
    db.commit()
    work = cursor.fetchall()[0]
    count_work_sql = "select count(*) from WORK WHERE work_name='%s'" % work[1]
    cursor.execute(count_work_sql)
    db.commit()
    count = cursor.fetchall()[0]
    version_s = str(count[0] + 1)
    work_name = work[1]
    work_status = '未开始'
    extend1 = 'null'

    extend2 = json.dumps(work[4])
    extend3 = 'null'
    belong_sys = work[6]
    end_time = 'null'
    run_way = work[8]
    start_time = 'null'
    temp_id = work[10]
    total_time = 'null'
    value_list = json.dumps(work[12], ensure_ascii=False)
    x_13 = ''
    if work[13] is None:
        x_13 = 'null'
    zip_name = x_13
    build_time = str(get_timestamp())
    version = version_s
    work_type = work[16]

    if work[17] is None:
        x_17 = 'null'
        jar_name = x_17
    else:
        jar_name = work[17]

    publish_way = work[18]
    time_rule = work[19]

    if work[20] is None:
        x_20 = 'null'
        webapps_name = x_20
    else:
        webapps_name=work[20]

    create_work_sql = "insert into work values('%s','%s','%s',%s,%s,%s,'%s',%s,'%s',%s,'%s',%s,%s,%s,%s,'%s','%s','%s','%s','%s','%s')" \
                      %('?',work_name, work_status, extend1, extend2, extend3, belong_sys, end_time,
                         run_way, start_time, temp_id, total_time, value_list, zip_name, build_time,
                         version, work_type, jar_name, publish_way, time_rule, webapps_name)

    cursor.execute(create_work_sql)
    db.commit()
    select_id = "select id from work ORDER  BY id desc"
    cursor.execute(select_id)
    next_id = cursor.fetchall()[0][0]
    db.commit()
    cursor.close()
    db.close()
    return next_id

# if __name__ == '__main__':
#     idd = create_and_run('10110')
#     print(idd)
