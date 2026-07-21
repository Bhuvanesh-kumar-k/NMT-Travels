#!/bin/bash
# Render startup script - runs migrations before starting server
python manage.py migrate --noinput
python manage.py init_admin
python manage.py collectstatic --noinput
gunicorn nmt_travels.wsgi:application
