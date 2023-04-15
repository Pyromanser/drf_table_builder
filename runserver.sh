#!/usr/bin/env sh

set -o errexit
set -o nounset

echo "Run manage.py migrate"
python manage.py migrate --noinput

#echo "Flushing database"
#python manage.py flush --noinput
echo "Importing test data"
python manage.py loaddata fixtures.json

echo "Run server"
exec  python -Wd manage.py runserver 0.0.0.0:8000