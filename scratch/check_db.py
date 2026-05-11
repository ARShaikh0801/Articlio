import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Articlio.settings')
django.setup()

from django.db import connections
from django.db.utils import OperationalError

db_conn = connections['default']
try:
    db_conn.cursor()
    print(f"Successfully connected to database: {db_conn.settings_dict['ENGINE']}")
    print(f"Database Name: {db_conn.settings_dict['NAME']}")
    print(f"Host: {db_conn.settings_dict.get('HOST', 'Local')}")
except OperationalError as e:
    print(f"Error connecting to database: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
