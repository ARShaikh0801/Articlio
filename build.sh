#!/bin/bash
set -o errexit

pip install -r requirements.txt

npm install

# Set PATH so collectstatic can find the node executable
export PATH="/opt/render/project/src/node_modules/.bin:$PATH"

python manage.py collectstatic --no-input
