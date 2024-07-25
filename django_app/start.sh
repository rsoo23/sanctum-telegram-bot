#! /usr/bin/env bash

python manage.py makemigrations
python manage.py migrate

# Directory to check
DIRECTORY="/app/staticfiles"

# Check if the directory exists
if [ -d "$DIRECTORY" ]; then
  echo "Directory $DIRECTORY exists."
else
  echo "Directory $DIRECTORY does not exist. Running collectstatic..."
  python manage.py collectstatic --noinput
fi

# python manage.py runserver 0.0.0.0:8000
# daphne -b 0.0.0.0 -p 8000 sanctum.asgi:application

watchmedo auto-restart --directory=/app --pattern=*.py --recursive -- daphne -b 0.0.0.0 -p 8000 sanctum.asgi:application
