from django.test import TestCase
from confManage.models import *


# Create your tests here.

class confManageTest(TestCase):
    def get(self):
        print (HostInfo.objects.all())