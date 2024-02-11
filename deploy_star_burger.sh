#!/bin/bash
set -e

source .env

cd /opt/star-burger
git pull

python3 -m venv venv 
echo "Created venv"

source venv/bin/activate
echo "Activated venv"

pip3 install -r requirements.txt
echo "Installed libraries"

python3 manage.py collectstatic --noinput
echo "Created static"

python3 manage.py migrate
echo "Made migrate"

npm ci --dev
echo "Installed Node.js"

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Built frontend"

systemctl restart starburger.service
systemctl reload nginx.service
echo "Restarted system services"


commit=$(git rev-parse master)

curl -H "X-Rollbar-Access-Token: $ROLLBAR_KEY" \
     -H "accept: application/json" \
     -H "content-type: application/json" \
     -X POST "https://api.rollbar.com/api/1/deploy" \
     -d '{
  "environment": "production",
  "revision": "'"$commit"'",
  "rollbar_username": "'$(whoami)'",
  "local_username": "'$(whoami)'",
  "comment": "deploy",
  "status": "succeeded"
}'
echo "Sent information to Rollbar"

deactivate
echo "Deactivated venv"

echo "Deployment completed successfully!"

