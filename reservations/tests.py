from django.test import TestCase
from django.contrib.auth.models import User
from .models import Room, Building, Reservation
from .utils import is_conflict
from datetime import datetime, timedelta

class ReservationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.building = Building.objects.create(name="Main")
        self.room = Room.objects.create(name="101", building=self.building)

    def test_valid_reservation(self):
        start = datetime.now()
        end = start + timedelta(hours=1)

        self.assertFalse(is_conflict(self.room, start, end))

    def test_conflicting_reservation(self):
        start = datetime.now()
        end = start + timedelta(hours=2)

        Reservation.objects.create(
            user=self.user,
            room=self.room,
            start_time=start,
            end_time=end
        )

        self.assertTrue(is_conflict(self.room, start, end))