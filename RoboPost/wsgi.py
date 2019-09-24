#!/usr/bin/python
"""
WSGI config for RoboPost project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""
import os
import django
from django.core.wsgi import get_wsgi_application
# from work.models import WorkInfo
# from tool.timing import add_time
# from work.views import run_work_time
# from datetime import datetime
# import logging
# log = logging.getLogger('autoops')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RoboPost.settings")
django.setup()
application = get_wsgi_application()
