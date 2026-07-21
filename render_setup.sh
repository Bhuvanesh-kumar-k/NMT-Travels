#!/bin/bash
# Render deployment setup script
python manage.py migrate
python manage.py init_admin
