from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from rooms.models import Building, Room

from .models import Reservation, has_approved_overlap


class ApprovedOverlapTests(TestCase):
    """Conflict checks only consider approved reservations."""

    def setUp(self):
        self.user = User.objects.create(username="u1")
        self.building = Building.objects.create(name="Main")
        self.room = Room.objects.create(
            building=self.building,
            number="101",
            capacity=20,
        )
        self.start = timezone.now()
        self.end = self.start + timedelta(hours=2)

    def test_no_overlap_when_empty(self):
        self.assertFalse(has_approved_overlap(self.room, self.start, self.end))

    def test_pending_does_not_block(self):
        Reservation.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.start,
            end_time=self.end,
            status=Reservation.Status.PENDING,
        )
        self.assertFalse(has_approved_overlap(self.room, self.start, self.end))

    def test_approved_blocks_overlap(self):
        Reservation.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.start,
            end_time=self.end,
            status=Reservation.Status.APPROVED,
        )
        self.assertTrue(has_approved_overlap(self.room, self.start, self.end))


class ReservationAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="alice", password="pw")
        self.staff = User.objects.create_user(
            username="staffer", password="pw", is_staff=True
        )
        self.building = Building.objects.create(name="NAC")
        self.room = Room.objects.create(
            building=self.building, number="1/202", capacity=30
        )
        self.t0 = timezone.now()
        self.t1 = self.t0 + timedelta(hours=1)

    def test_post_requires_login(self):
        r = self.client.post(
            "/reservations/",
            data='{"room_id": 1, "start_time": "2026-01-01T10:00:00Z", "end_time": "2026-01-01T11:00:00Z"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 401)

    def test_post_creates_pending(self):
        self.client.login(username="alice", password="pw")
        r = self.client.post(
            "/reservations/",
            data={
                "room_id": self.room.pk,
                "start_time": self.t0.isoformat(),
                "end_time": self.t1.isoformat(),
            },
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        data = r.json()
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["user_id"], self.user.pk)

    def test_get_lists_own_only(self):
        other = User.objects.create_user(username="bob", password="pw")
        Reservation.objects.create(
            user=other,
            room=self.room,
            start_time=self.t0,
            end_time=self.t1,
            status=Reservation.Status.PENDING,
        )
        mine = Reservation.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.t0 + timedelta(days=1),
            end_time=self.t1 + timedelta(days=1),
            status=Reservation.Status.PENDING,
        )
        self.client.login(username="alice", password="pw")
        r = self.client.get("/reservations/")
        self.assertEqual(r.status_code, 200)
        ids = [x["id"] for x in r.json()["reservations"]]
        self.assertIn(mine.pk, ids)
        self.assertEqual(len(ids), 1)

    def test_patch_approve_staff_only(self):
        res = Reservation.objects.create(
            user=self.user,
            room=self.room,
            start_time=self.t0,
            end_time=self.t1,
            status=Reservation.Status.PENDING,
        )
        self.client.login(username="alice", password="pw")
        r = self.client.patch(
            f"/reservations/{res.pk}/",
            data='{"status": "approved"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 403)

        self.client.login(username="staffer", password="pw")
        r = self.client.patch(
            f"/reservations/{res.pk}/",
            data='{"status": "approved"}',
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "approved")
