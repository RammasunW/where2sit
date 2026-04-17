from django.core.management.base import BaseCommand
from rooms.models import Building, Room
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Seed the database with sample data"

    @staticmethod
    def create_room(building, number, capacity):
        Room.objects.create(building=building, number=number, capacity=capacity)

    @staticmethod
    def create_user(username, password):
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password=password)

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
        self.create_room(b1, "6/112", 30)
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

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
