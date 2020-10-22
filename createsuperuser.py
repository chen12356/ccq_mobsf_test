#!/usr/bin/env python3
import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobSF.settings')
django.setup()

from MobSF.models import User

USERNAME = 'admin'
EMAIl = ''
PASSWORD = 'admin123'
if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIl, PASSWORD)
else:
    print('User "{}" exists already, not created'.format(USERNAME))
