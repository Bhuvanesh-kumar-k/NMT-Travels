#!/bin/bash

# NMT Travels Deployment Script for PythonAnywhere
# This script deploys the Django backend to PythonAnywhere

set -e

echo "Starting deployment to PythonAnywhere..."

# Configuration
PYTHONANYWHERE_USERNAME="${PYTHONANYWHERE_USERNAME:-yourusername}"
PROJECT_DIR="/home/${PYTHONANYWHERE_USERNAME}/nmt-travels"
VENV_DIR="${PROJECT_DIR}/venv"
DJANGO_SETTINGS_MODULE="nmt_travels.settings"

# Navigate to project directory
cd "${PROJECT_DIR}" || exit 1

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Reload the web application
echo "Reloading web application..."
touch "/var/www/${PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py"

echo "Deployment completed successfully!"

