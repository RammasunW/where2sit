from django.test import Client

class ReservationAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="123")
        self.client.login(username="test", password="123")

    def test_create_reservation_api(self):
        response = self.client.post("/reserve/", {
            "room_id": 1,
            "start_time": "2026-03-20T10:00:00",
            "end_time": "2026-03-20T11:00:00"
        }, content_type="application/json")

        self.assertEqual(response.status_code, 200)s