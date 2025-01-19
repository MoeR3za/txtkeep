#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the container
echo "Starting the application..."
gunicorn txtkeep.wsgi:application --bind 0.0.0.0:8000
