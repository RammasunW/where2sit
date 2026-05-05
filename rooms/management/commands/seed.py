from django.core.management.base import BaseCommand
from rooms.models import Building, Room, RoomRating, ClassSchedule
from django.contrib.auth.models import User
from datetime import time


class Command(BaseCommand):
    help = "Seed the database with sample data"

    @staticmethod
    def create_room(building, number, capacity):
        return Room.objects.create(building=building, number=number, capacity=capacity)

    @staticmethod
    def create_user(username, password):
        if not User.objects.filter(username=username).exists():
            return User.objects.create_user(username=username, password=password)

    @staticmethod
    def create_class(room, day, start, end, name):
        return ClassSchedule.objects.create(room=room,
                                     day_of_week=day,
                                     start_time=start,
                                     end_time=end,
                                     course_name=name)

    def handle(self, *args, **kwargs):

        # Create users
        self.create_user("alice", "password123")
        self.create_user("bob", "password123")
        self.create_user("charlie", "password123")

        # Create rooms
        Building.objects.all().delete()
        Room.objects.all().delete()

        b1 = Building.objects.create(name="NAC")
        b2 = Building.objects.create(name="Shepard Hall")
        b3 = Building.objects.create(name="Marshak")
        b4 = Building.objects.create(name="Steinman")

        # NAC
        self.create_room(b1, "1/203", 90)
        self.create_room(b1, "1/511E", 35)
        self.create_room(b1, "4/113", 40)
        self.create_room(b1, "6/111", 40)
        NAC6112 = self.create_room(b1, "6/112", 30)
        self.create_room(b1, "6/113", 40)
        self.create_room(b1, "6/121", 30)
        self.create_room(b1, "6/310", 30)
        self.create_room(b1, "7/313A", 30)

        # SH
        self.create_room(b2, "201", 30)
        self.create_room(b2, "210", 45)
        self.create_room(b2, "203", 30)
        self.create_room(b2, "204", 30)
        self.create_room(b2, "378", 30)

        # Marshak
        self.create_room(b3, "410", 30)
        self.create_room(b3, "1307", 30)
        self.create_room(b3, "1026", 30)
        self.create_room(b3, "1123", 30)
        self.create_room(b3, "MR1", 100)
        self.create_room(b3, "MR2", 240)
        self.create_room(b3, "MR3", 240)


        # Steinman
        self.create_room(b4, "161", 100)

        # Add class schedule for some rooms
        self.create_class(NAC6112, 1, time(14,0), time(15,15), "MATH 30800")
        self.create_class(NAC6112, 3, time(14,0), time(15,15), "MATH 30800")

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
