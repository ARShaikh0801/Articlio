#!/bin/bash
set -o errexit

pip install -r requirements.txt

npm install
chmod -R +x node_modules/.bin/
npm run build:min

# Set PATH so collectstatic can find the node executable
export PATH="/opt/render/project/src/node_modules/.bin:$PATH"

python manage.py collectstatic --no-input

