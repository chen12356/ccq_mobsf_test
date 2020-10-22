#!/bin/bash
# Dev Server
#. venv/bin/activate && python manage.py runserver
# Prod Server
#. venv/bin/activate && gunicorn -b 0.0.0.0:8000 MobSF.wsgi:application --workers=1 --threads=10 --timeout=1800
service mysql start&& redis-service /etc/redis/redis.conf
gunicorn -b 0.0.0.0:8000 MobSF.wsgi:application --workers=1 --threads=10 --timeout=1800
