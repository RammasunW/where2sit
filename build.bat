@echo off
echo Installing requirements...
pip install -r requirements.txt

echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo Seeding database...
python manage.py import_classes
python manage.py seed

echo Building assets...
python manage.py tailwind build

echo Setup complete!
python manage.py runserver
