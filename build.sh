#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Run Django commands
python manage.py collectstatic --noinput --clear

# Create the static directory if it doesn't exist
mkdir -p staticfiles
