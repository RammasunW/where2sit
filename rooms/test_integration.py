import pytest
from django.test import Client, RequestFactory
from rooms.models import Building, Room
from rooms.views import room_list


# =====================================================
# INTEGRATION TESTS - Testing View + Model interaction
# =====================================================

@pytest.mark.django_db
class TestRoomListViewModelIntegration:
    """Integration tests for the room_list view interacting with the Room/Building models"""

    def test_view_returns_rooms_from_database(self):
        """The room_list view should query Room objects from the database
        and pass them to the template context"""
        building = Building.objects.create(name="NAC")
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=25)

        client = Client()
        response = client.get("/")

        assert response.status_code == 200
        # Verify the view passes the correct rooms in context
        rooms_in_context = list(response.context["rooms"])
        assert len(rooms_in_context) == 2
        assert room1 in rooms_in_context
        assert room2 in rooms_in_context

    def test_view_reflects_database_changes(self):
        """After adding and then deleting a room, the view should reflect
        the current database state"""
        building = Building.objects.create(name="Shepard Hall")
        room = Room.objects.create(building=building, number="101", capacity=40)

        client = Client()

        # Room should appear
        response = client.get("/")
        content = response.content.decode()
        assert "Shepard Hall" in content
        assert "101" in content

        # Delete the room - view should no longer show it
        room.delete()
        response = client.get("/")
        content = response.content.decode()
        assert "101" not in content

    def test_view_displays_room_building_relationship(self):
        """The view should correctly display the building name associated
        with each room through the ForeignKey relationship"""
        nac = Building.objects.create(name="NAC")
        marshak = Building.objects.create(name="Marshak")
        Room.objects.create(building=nac, number="1/202", capacity=30)
        Room.objects.create(building=marshak, number="301", capacity=40)

        client = Client()
        response = client.get("/")
        content = response.content.decode()

        assert "NAC" in content
        assert "Marshak" in content
        assert "1/202" in content
        assert "301" in content

    def test_view_handles_cascade_delete_from_building(self):
        """When a building is deleted, its rooms should be cascade deleted,
        and the view should handle this gracefully (error condition)"""
        building = Building.objects.create(name="Temporary Hall")
        Room.objects.create(building=building, number="100", capacity=20)
        Room.objects.create(building=building, number="101", capacity=25)

        client = Client()

        # Verify rooms appear
        response = client.get("/")
        assert "Temporary Hall" in response.content.decode()

        # Cascade delete - this tests the interaction between the model's
        # CASCADE behavior and the view rendering
        building.delete()
        assert Room.objects.count() == 0

        # View should still work with no rooms
        response = client.get("/")
        assert response.status_code == 200
        assert "Temporary Hall" not in response.content.decode()

    def test_view_with_request_factory(self):
        """Test the view function directly using RequestFactory to verify
        it correctly interacts with the model layer"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="6/114", capacity=50)

        factory = RequestFactory()
        request = factory.get("/")
        response = room_list(request)

        assert response.status_code == 200
        content = response.content.decode()
        assert "NAC" in content
        assert "6/114" in content