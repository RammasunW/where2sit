from pathlib import Path
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from rooms.models import (
    Building,
    Room,
    ClassSchedule
)

import re
from datetime import datetime

bad_room_name = ["TBA",
                 "ONLINE",
                 "25 Bway 7-15",
                 "25 Bway 7-25",
                 "Off-Campus",
                 "Online-Synchronous",
                 ]

DAY_MAP = {
    "Mo": 0,
    "Tu": 1,
    "We": 2,
    "Th": 3,
    "Fr": 4,
    "Sa": 5,
    "Su": 6,
}


BUILDING_MAP = {
    "NAC": "NAC",
    "Shepard": "Shepard Hall",
    "Marshak": "Marshak",
    "Steinman": "Steinman",
    "Baskerville Hall": "Baskerville Hall",
    "Baskervill": "Baskerville Hall",
    "AaronDavis": "Aaron Davis Hall",
    "Comp Goeth": "Compton-Goethals Hall",
    "Wingate": "Wingate Hall",
    "Harris": "Townsend Harris Hall",
    "SSA": "Spitzer Hall",
}


class Command(BaseCommand):

    help = "Import all class schedules"

    def handle(self, *args, **kwargs):

        total = 0

        # OPTIONAL
        ClassSchedule.objects.all().delete()
        Building.objects.all().delete()

        # Create buildings
        for b in BUILDING_MAP:
            Building.objects.create(name=BUILDING_MAP[b])

        data_dir = Path("rooms/data/")

        html_files = data_dir.glob("*.html")

        for html_file in html_files:

            print(f"\nProcessing {html_file}")

            total += self.import_file(html_file)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nImported {total} schedules total"
            )
        )

    def import_file(self, filepath):

        count = 0

        try:
            with open(filepath, encoding="utf-8") as f:
                html = f.read()

        except UnicodeDecodeError:

            with open(filepath, encoding="latin-1") as f:
                html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        sections = soup.find_all(
            "div",
            class_="testing_msg"
        )

        for section in sections:

            course_text = section.get_text(
                " ",
                strip=True
            )

            # Generic parser
            course_match = re.search(
                r"([A-Z]{2,5})\s*(\d+[A-Z]*)\s*-\s*(.*)",
                course_text
            )

            if not course_match:
                continue

            department = course_match.group(1)
            course_number = course_match.group(2)
            course_name = course_match.group(3)

            table = section.find_next("table")

            if not table:
                continue

            rows = table.find_all("tr")

            for row in rows:

                cols = row.find_all("td")

                if len(cols) < 9:
                    continue

                try:

                    section_name = cols[1].get_text(strip=True)

                    times_list = [
                        BeautifulSoup(x, "html.parser").get_text(strip=True)
                        for x in cols[2].decode_contents().split("<br/>")
                    ]

                    rooms_list = [
                        BeautifulSoup(x, "html.parser").get_text(strip=True)
                        for x in cols[3].decode_contents().split("<br/>")
                    ]

                    instructors_list = [
                        BeautifulSoup(x, "html.parser").get_text(strip=True)
                        for x in cols[4].decode_contents().split("<br/>")
                    ]

                    for i in range(len(times_list)):
                        days_times = times_list[i]

                        room_text = (
                            rooms_list[i]
                            if i < len(rooms_list)
                            else rooms_list[0]
                        )

                        instructor = (
                            instructors_list[i]
                            if i < len(instructors_list)
                            else instructors_list[0]
                        )

                        if (
                            room_text in bad_room_name
                            or not days_times
                        ):
                            continue

                        # Example:
                        # TuTh 9:30AM - 10:45AM

                        match = re.match(
                            r"([A-Za-z]+)\s+"
                            r"(\d+:\d+[AP]M)\s*-\s*"
                            r"(\d+:\d+[AP]M)",
                            days_times
                        )

                        if not match:
                            continue

                        day_str = match.group(1)

                        start_time = datetime.strptime(
                            match.group(2),
                            "%I:%M%p"
                        ).time()

                        end_time = datetime.strptime(
                            match.group(3),
                            "%I:%M%p"
                        ).time()

                        building_short = None
                        room_number = None

                        # Match longest building name first
                        for key in sorted(
                                BUILDING_MAP.keys(),
                                key=len,
                                reverse=True
                        ):

                            if room_text.startswith(key):
                                building_short = key

                                room_number = room_text[len(key):].strip()

                                break

                        if not building_short or not room_number:
                            print("Could not parse room:", room_text)

                            continue

                        building_name = BUILDING_MAP.get(
                            building_short,
                            building_short
                        )

                        building = Building.objects.filter(
                            name__icontains=building_name
                        ).first()

                        if not building:
                            continue

                        room = Room.objects.filter(
                            building=building,
                            number=room_number
                        ).first()

                        if not room:
                            room = Room.objects.create(
                                building=building,
                                number=room_number,
                                capacity=30,
                            )

                        days = re.findall(
                            r"Mo|Tu|We|Th|Fr|Sa|Su",
                            day_str
                        )

                        for d in days:

                            ClassSchedule.objects.get_or_create(
                                room=room,

                                #department=department,

                                #course_number=course_number,

                                course_name=department + course_number + ' - ' + course_name,

                                #section=section_name,

                                #instructor=instructor,

                                day_of_week=DAY_MAP[d],

                                start_time=start_time,

                                end_time=end_time,
                            )

                            count += 1

                except Exception as e:

                    print(
                        f"ERROR in {filepath}:",
                        e
                    )

        print(f"Imported {count} entries")

        return count