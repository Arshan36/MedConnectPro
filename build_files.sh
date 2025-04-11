#!/bin/bash

# Install dependencies
pip install -r vercel-requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate