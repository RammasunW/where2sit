#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py migrate
python manage.py tailwind build
python manage.py collectstatic --noinput