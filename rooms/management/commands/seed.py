from django.core.management.base import BaseCommand
from rooms.models import *
from django.contrib.auth.models import User, Group
from datetime import time, date


class Command(BaseCommand):
    help = "Seed the database with sample data"

    @staticmethod
    def create_room(building, number, capacity, floor):
        return Room.objects.create(building=building, number=number, capacity=capacity, floor=floor)

    @staticmethod
    def create_user(username, password):
        if not User.objects.filter(username=username).exists():
            return User.objects.create_user(username=username, password=password)
        else:
            return User.objects.get(username=username)

    @staticmethod
    def create_class(room, day, start, end, name):
        return ClassSchedule.objects.create(room=room,
                                     day_of_week=day,
                                     start_time=start,
                                     end_time=end,
                                     course_name=name)

    @staticmethod
    def create_reservation(user, room, date, start_time, end_time):
        return Reservation.objects.create(
            user=user,
            room=room,
            date=date,
            start_time=start_time,
            end_time=end_time,
        )

    def handle(self, *args, **kwargs):

        # Manager role users
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        
        # Create users
        alice = self.create_user("alice", "password123")
        self.create_user("bob", "password123")
        charlie = self.create_user("charlie", "password123")

        charlie.groups.add(manager_group)

        # Create rooms
        Building.objects.all().delete()
        Room.objects.all().delete()

        b1 = Building.objects.create(name="NAC")
        b2 = Building.objects.create(name="Shepard Hall")
        b3 = Building.objects.create(name="Marshak")
        b4 = Building.objects.create(name="Steinman")

        # NAC
        self.create_room(b1, "1/203", 90, 2)
        self.create_room(b1, "1/511E", 35, 1)
        self.create_room(b1, "4/113", 40, 4)
        self.create_room(b1, "6/111", 40, 6)
        NAC6112 = self.create_room(b1, "6/112", 30, 6)
        self.create_room(b1, "6/113", 40, 6)
        self.create_room(b1, "6/121", 30, 6)
        self.create_room(b1, "6/310", 30, 6)
        self.create_room(b1, "7/313A", 30, 7)

        # SH
        self.create_room(b2, "201", 30, 2)
        self.create_room(b2, "210", 45, 2)
        self.create_room(b2, "203", 30, 2)
        self.create_room(b2, "204", 30, 2)
        self.create_room(b2, "378", 30, 3)

        # Marshak
        self.create_room(b3, "410", 30, 4)
        self.create_room(b3, "1307", 30, 13)
        self.create_room(b3, "1026", 30, 10)
        self.create_room(b3, "1123", 30, 11)
        self.create_room(b3, "MR1", 100, 1)
        self.create_room(b3, "MR2", 240, 1)
        self.create_room(b3, "MR3", 240, 1)


        # Steinman
        self.create_room(b4, "161", 100, 1)

        # Add class schedule for some rooms
        # 0 = Mon, 1 = Tue, 2 = Wed, 3 = Thu, 4 = Fri, 5 = Sat, 6 = Sun
        self.create_class(NAC6112, 0, time(17,0), time(18,15), "ECO 10002")
        self.create_class(NAC6112, 2, time(17,0), time(18,15), "ECO 10002")
        self.create_class(NAC6112, 0, time(18,45), time(20,0), "EE 21000")
        self.create_class(NAC6112, 2, time(18,45), time(20,0), "EE 21000")
        self.create_class(NAC6112, 0, time(9,30), time(10,45), "SPAN 10100")
        self.create_class(NAC6112, 2, time(9,30), time(10,45), "SPAN 10100")
        self.create_class(NAC6112, 0, time(14,0), time(15,40), "MATH 32404")
        self.create_class(NAC6112, 2, time(14,0), time(15,40), "MATH 32404")
        self.create_class(NAC6112, 0, time(11,0), time(12,15), "SOC 26800")
        self.create_class(NAC6112, 2, time(11,0), time(12,15), "SOC 26800")
        self.create_class(NAC6112, 0, time(12,30), time(13,45), "WHUM 10100")
        self.create_class(NAC6112, 2, time(12,30), time(13,45), "WHUM 10100")
        self.create_class(NAC6112, 1, time(9,30), time(10,45), "MATH 15000")
        self.create_class(NAC6112, 3, time(9,30), time(10,45), "MATH 15000")
        self.create_class(NAC6112, 1, time(11,0), time(12,15), "PHIL 10200")
        self.create_class(NAC6112, 3, time(11,0), time(12,15), "PHIL 10200")
        self.create_class(NAC6112, 1, time(15,30), time(16,45), "PHIL 30500")
        self.create_class(NAC6112, 3, time(15,30), time(16,45), "PHIL 30500")
        self.create_class(NAC6112, 1, time(14,0), time(15,15), "MATH 30800")
        self.create_class(NAC6112, 3, time(14,0), time(15,15), "MATH 30800")
        self.create_class(NAC6112, 3, time(17,0), time(19,30), "ECO 43250")

        # Add sample ratings for some rooms
        from random import randint, choice
        users = list(User.objects.filter(username__in=["alice", "bob", "charlie"]))
        rooms = list(Room.objects.all())
        comments = [
            "Great room!",
            "Very quiet and comfortable.",
            "Too noisy sometimes.",
            "Perfect for group study.",
            "Nice lighting.",
            "Needs more power outlets."
        ]
        # Each user rates 3 random rooms
        for user in users:
            for room in rooms[:3]:
                RoomRating.objects.update_or_create(
                    user=user, room=room,
                    defaults={
                        "score": randint(3, 5),
                        "comment": choice(comments)
                    }
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
