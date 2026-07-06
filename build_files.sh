#!/bin/bash
echo "Building the project..."
python3.9 -m pip install -r requirements.txt

echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Running migrations..."
python3.9 manage.py migrate --noinput