#!/bin/bash

# Make sure we're in the project root
cd /opt/render/project/src

# Upgrade pip and install setuptools
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Run Django commands
python manage.py collectstatic --noinput
python manage.py migrate --noinput
