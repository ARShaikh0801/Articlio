#!/bin/bash
set -o errexit

pip install -r requirements.txt

npm install

python manage.py collectstatic --no-input

# This ensures your Django project can find the node command in the Cloud Run environment
import os
os.environ['PATH'] = "/workspace/node_modules/.bin:/workspace:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Then, when collectstatic runs, it will find the node executable.
