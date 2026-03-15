import pytest
from django.test import Client
from rooms.models import Building, Room


# =====================================================
# MODEL TESTS - Testing the Building and Room models
# =====================================================

@pytest.mark.django_db
class TestBuildingModel:
    """Tests for the Building model"""

    def test_create_building(self):
        """A building can be created with a name"""
        building = Building.objects.create(name="NAC")
        assert building.name == "NAC"
        assert Building.objects.count() == 1

    def test_building_str(self):
        """Building __str__ returns the building name"""
        building = Building.objects.create(name="Shepard Hall")
        assert str(building) == "Shepard Hall"

    def test_building_name_max_length(self):
        """Building name field has max_length of 100"""
        name_field = Building._meta.get_field('name')
        assert name_field.max_length == 100


@pytest.mark.django_db
class TestRoomModel:
    """Tests for the Room model"""

    def test_create_room(self):
        """A room can be created with a building, number, and capacity"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        assert room.building == building
        assert room.number == "1/202"
        assert room.capacity == 30
        assert Room.objects.count() == 1

    def test_room_str(self):
        """Room __str__ returns 'Building - Number' format"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="4/220", capacity=50)
        assert str(room) == "NAC - 4/220"

    def test_room_belongs_to_building(self):
        """Room has a foreign key relationship to Building"""
        building = Building.objects.create(name="Marshak")
        room = Room.objects.create(building=building, number="301", capacity=40)
        assert room.building.name == "Marshak"

    def test_room_cascade_delete(self):
        """Deleting a building deletes its rooms"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        Room.objects.create(building=building, number="1/203", capacity=25)
        assert Room.objects.count() == 2
        building.delete()
        assert Room.objects.count() == 0


# =====================================================
# VIEW TESTS - Testing the room_list view
# =====================================================

@pytest.mark.django_db
class TestRoomListView:
    """Tests for the room_list view"""

    def test_room_list_returns_200(self):
        """The room list page should return a 200 status code"""
        client = Client()
        response = client.get("/")
        assert response.status_code == 200

    def test_room_list_uses_correct_template(self):
        """The room list view should use rooms/room_list.html"""
        client = Client()
        response = client.get("/")
        assert "rooms/room_list.html" in [t.name for t in response.templates]

    def test_room_list_displays_rooms(self):
        """Rooms in the database should appear in the response"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        assert "NAC" in content
        assert "1/202" in content
        assert "30" in content

    def test_room_list_empty(self):
        """The page should still load when there are no rooms"""
        client = Client()
        response = client.get("/")
        assert response.status_code == 200

    def test_room_list_multiple_rooms(self):
        """Multiple rooms should all appear"""
        nac = Building.objects.create(name="NAC")
        shepard = Building.objects.create(name="Shepard Hall")
        Room.objects.create(building=nac, number="1/202", capacity=30)
        Room.objects.create(building=shepard, number="101", capacity=60)
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        assert "NAC" in content
        assert "Shepard Hall" in content


# =====================================================
# SANITY TEST
# =====================================================

def test_sanity():
    """Basic sanity check that pytest is working"""
    assert True