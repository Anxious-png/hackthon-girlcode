#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting gunicorn..."
gunicorn silentguard.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
