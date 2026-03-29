# where2sit

A campus room availability tracker

## Pitch

Don't know where to go when you have an online class? The quiet floor in the library is too loud? Too shy to sit next to strangers? We got you!

Currently we don't have a centralized system to view room availability. This tracker is a web-based application that provides faculty, student, and clubs with clear overview of room availability at a specific time. By leveraging class data and room assignments, the system helps individuals and organizations find open spaces for studying or meetings, making sure everyone gets a pleasant environment.

## Description

where2sit is designed to make campus space usage more visible and flexible. It maintains a database of reserved rooms with scheduled classes and other events. It provides accurate, up-to-date availability information based on verified user input. Users can search for rooms by time, location, capacity, and available resources (e.g. number of blackboards) to find an unoccupied room that best fits their need. Users can rate and leave comments on a room. They can also report issues (e.g. projector is not working) and relevant staff will be notified. In case of emergency, this program provides the fastest evacuation route.

Users can request room usage and it will be processed by authorized members. They will be notified if there is a change to their assigned room. Authorized members (such as staff) can manage room data and scheduled events, ensuring all information is accurate.

## Primary Users

- Students looking for empty spaces to self-study or attend online classes
- Organizations/clubs planning meetings or events
- Faculty and staff needing visibility into room availability or managing room assignments

## Features

- View room availability by date and time
- View directions to and evacuation routes of rooms
- Filter rooms by building, capacity, available resources, ratings, and more
- Display scheduled classes and other reserved time slots
- Administrative interface for mananging rooms

## Benefits

- Utilizes campus resources wisely
- Makes it faster to search for empty spaces
- Avoids room availability conflicts
- Provides alternative to libraries and common areas

## Developer Side / Notes

## How to run application

Something like the following for instructions on how to run:

1 Clone repo
2 Create virtual environment
3 Install requirements
4 Run migrations
5 Start development server

Clearer Setup:
git clone repo
cd where2sit

python -m venv venv # Only if virtual environment not already set up.
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
(python manage.py tailwind start) #In separate Teminal/If making frontend changes
python manage.py runserver
