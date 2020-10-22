#!/bin/bash

REMOTE_DIR="/root/Mobile-Security-Framework-MobSF"
cd $REMOTE_DIR

python3 manage.py makemigrations && \
python3 manage.py makemigrations MobSF&& \
python3 manage.py makemigrations StaticAnalyzer && \
python3 manage.py migrate && \
python3 $REMOTE_DIR/sdk_data/test_one.py
./createsuperuser.py

gunicorn -b 0.0.0.0:8000 MobSF.wsgi:application --workers=1 --threads=10 --timeout=1800