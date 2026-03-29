from django.core.management.base import BaseCommand
from rooms.models import Building, Room

def create_room(building, number, capacity):
    Room.objects.create(building=building, number=number, capacity=capacity)

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        Building.objects.all().delete()
        Room.objects.all().delete()

        b1 = Building.objects.create(name="NAC")
        b2 = Building.objects.create(name="Shepard Hall")
        b3 = Building.objects.create(name="Marshak")

        # NAC
        create_room(b1, "0/201", 60)
        create_room(b1, "4/113", 40)
        create_room(b1, "6/111", 40)
        create_room(b1, "6/112", 30)
        create_room(b1, "6/113", 40)
        create_room(b1, "6/310", 30)
        create_room(b1, "7/313A", 30)

        # SH
        create_room(b2, "201", 30)
        create_room(b2, "204", 30)

        # Marshak
        create_room(b3, "1307", 30)
        create_room(b3, "1026", 30)
        create_room(b3, "1123", 30)
        create_room(b3, "MR1", 100)
        create_room(b3, "MR2", 240)
        create_room(b3, "MR3", 240)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
