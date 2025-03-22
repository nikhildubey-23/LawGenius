"""
WSGI config for LawGenius project.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
os.environ.setdefault('DJANGO_URLS_MODULE', 'urls')

app = get_wsgi_application()
