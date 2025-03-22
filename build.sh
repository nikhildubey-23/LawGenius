#!/bin/bash

# Make sure we're in the project root
cd /opt/render/project/src

# Set Python path
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Install Python 3.9
if ! command -v python3.9 &> /dev/null; then
    apt-get update && apt-get install -y python3.9 python3.9-dev python3.9-venv
fi

# Create and activate virtual environment
python3.9 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install setuptools
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Run Django commands
python manage.py collectstatic --noinput
python manage.py migrate --noinput
