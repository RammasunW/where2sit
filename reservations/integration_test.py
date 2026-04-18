import json

from django.contrib.auth.models import User
from django.test import TestCase

from rooms.models import Building, Room


class ReservationAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="123")
        b = Building.objects.create(name="Main")
        self.room = Room.objects.create(building=b, number="101", capacity=10)

    def test_create_reservation_api(self):
        self.client.login(username="test", password="123")
        payload = {
            "room_id": self.room.pk,
            "start_time": "2026-03-20T10:00:00+00:00",
            "end_time": "2026-03-20T11:00:00+00:00",
        }
        response = self.client.post(
            "/reservations/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "pending")
