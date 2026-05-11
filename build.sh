#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py import_classes
python manage.py seed
python manage.py tailwind build
python manage.py collectstatic --noinput