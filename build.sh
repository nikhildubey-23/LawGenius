#!/bin/bash

# Upgrade pip and install setuptools
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Run Django commands
python manage.py collectstatic --noinput --clear

# Create the static directory if it doesn't exist
mkdir -p staticfiles
