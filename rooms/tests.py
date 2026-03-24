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

    def test_building_empty_name(self):
        """Building can be created with an empty name (no validation enforced)"""
        building = Building.objects.create(name="")
        assert building.name == ""

    def test_building_duplicate_names_allowed(self):
        """Multiple buildings can have the same name (no unique constraint)"""
        Building.objects.create(name="NAC")
        Building.objects.create(name="NAC")
        assert Building.objects.filter(name="NAC").count() == 2

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

    def test_room_number_max_length(self):
        """Room number field has max_length of 10"""
        number_field = Room._meta.get_field('number')
        assert number_field.max_length == 10

    def test_room_capacity_is_integer(self):
        """Room capacity should store integer values correctly"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="101", capacity=0)
        assert room.capacity == 0

    def test_room_negative_capacity(self):
        """Room model currently accepts negative capacity (no validation).
        This test documents this behavior as a known gap."""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="101", capacity=-5)
        # The model doesn't enforce positive capacity - it saves without error
        assert room.capacity == -5

    def test_room_without_building_raises_error(self):
        """Creating a room without a building should raise an IntegrityError"""
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Room.objects.create(building=None, number="101", capacity=30)

    def test_room_str_with_special_characters(self):
        """Room __str__ handles building names with special characters"""
        building = Building.objects.create(name="O'Brien Hall")
        room = Room.objects.create(building=building, number="2/105", capacity=20)
        assert str(room) == "O'Brien Hall - 2/105"

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