import pytest
from django.test import Client, TestCase
from rooms.models import *
from django.contrib.auth.models import User
from datetime import date, time
from django.urls import reverse
import json

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
    
    def test_create_multiple_buildings(self):
        """Multiple buildings can be created"""
        Building.objects.create(name="NAC")
        Building.objects.create(name="Marshak")
        Building.objects.create(name="Steinman")
        assert Building.objects.count() == 3
    
    def test_building_name_empty_string(self):
        """Building can be created with empty name (edge case)"""
        building = Building.objects.create(name="")
        assert building.name == ""
    
    def test_building_name_with_special_characters(self):
        """Building name can contain special characters"""
        building = Building.objects.create(name="NAC-Building #1")
        assert building.name == "NAC-Building #1"


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
    
    def test_room_zero_capacity(self):
        """Room can have zero capacity (edge case)"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/100", capacity=0)
        assert room.capacity == 0
    
    def test_room_negative_capacity(self):
        """Room can have negative capacity (database allows it, validation should happen elsewhere)"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/100", capacity=-5)
        assert room.capacity == -5
    
    def test_room_large_capacity(self):
        """Room can have very large capacity"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="Auditorium", capacity=10000)
        assert room.capacity == 10000
    
    def test_room_number_field_max_length(self):
        """Room number field has max_length of 10"""
        number_field = Room._meta.get_field('number')
        assert number_field.max_length == 10
    
    def test_room_favorites_empty_by_default(self):
        """Room has no favorites when created"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        assert room.favorites.count() == 0
    
    def test_room_add_favorite_user(self):
        """User can be added to room favorites"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        room.favorites.add(user)
        assert room.favorites.count() == 1
        assert user in room.favorites.all()
    
    def test_room_multiple_favorites(self):
        """Multiple users can favorite the same room"""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        room.favorites.add(user1, user2)
        assert room.favorites.count() == 2
    
    def test_room_remove_favorite(self):
        """User can be removed from room favorites"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        room.favorites.add(user)
        assert room.favorites.count() == 1
        room.favorites.remove(user)
        assert room.favorites.count() == 0


@pytest.mark.django_db
class TestReservationModel:
    """Tests for the Reservation model"""
    
    def test_create_reservation(self):
        """A reservation can be created with all required fields"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        reservation = Reservation.objects.create(
            user=user,
            room=room,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        
        assert reservation.user == user
        assert reservation.room == room
        assert reservation.date == date(2026, 5, 15)
        assert reservation.start_time == time(10, 0)
        assert reservation.end_time == time(12, 0)
        assert Reservation.objects.count() == 1
    
    def test_reservation_with_name(self):
        """Reservation can have an optional name"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        reservation = Reservation.objects.create(
            user=user,
            room=room,
            name="Study Session",
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        
        assert reservation.name == "Study Session"
    
    def test_reservation_str_with_name(self):
        """Reservation __str__ includes name if provided"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        reservation = Reservation.objects.create(
            user=user,
            room=room,
            name="Study Session",
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        
        expected = "Study Session - NAC - 1/202 on 2026-05-15 from 10:00:00 to 12:00:00"
        assert str(reservation) == expected
    
    def test_reservation_str_without_name(self):
        """Reservation __str__ shows 'Anonymous' if no name"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        reservation = Reservation.objects.create(
            user=user,
            room=room,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        
        expected = "Anonymous - NAC - 1/202 on 2026-05-15 from 10:00:00 to 12:00:00"
        assert str(reservation) == expected
    
    def test_reservation_created_at_auto_set(self):
        """Reservation created_at is automatically set"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        reservation = Reservation.objects.create(
            user=user,
            room=room,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        
        assert reservation.created_at is not None
    
    def test_user_can_have_multiple_reservations(self):
        """A user can have multiple reservations"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=25)
        
        Reservation.objects.create(user=user, room=room1, date=date(2026, 5, 15), start_time=time(10, 0), end_time=time(12, 0))
        Reservation.objects.create(user=user, room=room2, date=date(2026, 5, 16), start_time=time(14, 0), end_time=time(15, 0))
        
        assert Reservation.objects.filter(user=user).count() == 2
    
    def test_room_can_have_multiple_reservations(self):
        """A room can have multiple reservations"""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        Reservation.objects.create(user=user1, room=room, date=date(2026, 5, 15), start_time=time(10, 0), end_time=time(12, 0))
        Reservation.objects.create(user=user2, room=room, date=date(2026, 5, 15), start_time=time(14, 0), end_time=time(15, 0))
        
        assert Reservation.objects.filter(room=room).count() == 2
    
    def test_reservation_cascade_delete_user(self):
        """Deleting a user deletes their reservations"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        Reservation.objects.create(user=user, room=room, date=date(2026, 5, 15), start_time=time(10, 0), end_time=time(12, 0))
        assert Reservation.objects.count() == 1
        
        user.delete()
        assert Reservation.objects.count() == 0
    
    def test_reservation_cascade_delete_room(self):
        """Deleting a room deletes its reservations"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        Reservation.objects.create(user=user, room=room, date=date(2026, 5, 15), start_time=time(10, 0), end_time=time(12, 0))
        assert Reservation.objects.count() == 1
        
        room.delete()
        assert Reservation.objects.count() == 0
    

    # obsolete: duration is no longer an attribute
    '''def test_reservation_duration_edge_cases(self):
        """Reservation can have various duration values"""
        user = User.objects.create_user(username="testuser", password="pass123")
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        # Duration of 1 hour
        r1 = Reservation.objects.create(user=user, room=room, date=date(2026, 5, 15), time=time(10, 0), duration=1)
        assert r1.duration == 1
        
        # Duration of 8 hours
        r2 = Reservation.objects.create(user=user, room=room, date=date(2026, 5, 16), time=time(9, 0), duration=8)
        assert r2.duration == 8'''


# =====================================================
# VIEW TESTS - Testing the views
# =====================================================

@pytest.mark.django_db
class TestHomeView:
    """Tests for the home view"""
    
    def test_home_returns_200(self):
        """The home page should return a 200 status code"""
        client = Client()
        response = client.get("/")
        assert response.status_code == 200
    
    def test_home_uses_correct_template(self):
        """The home view should use rooms/home.html"""
        client = Client()
        response = client.get("/")
        assert "rooms/home.html" in [t.name for t in response.templates]
    
    def test_home_context_has_buildings(self):
        """Home view context should include buildings"""
        Building.objects.create(name="NAC")
        Building.objects.create(name="Marshak")
        
        client = Client()
        response = client.get("/")
        
        assert 'buildings' in response.context
        assert response.context['buildings'].count() == 2
    
    def test_home_context_has_featured_rooms(self):
        """Home view context should include featured rooms"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        Room.objects.create(building=building, number="1/203", capacity=25)
        
        client = Client()
        response = client.get("/")
        
        # The view uses 'featured_rooms', but verify it exists
        assert 'featured_rooms' in response.context or 'top_rooms' in response.context
        
        # Use whichever key exists
        rooms_key = 'featured_rooms' if 'featured_rooms' in response.context else 'top_rooms'
        assert len(response.context[rooms_key]) <= 6  # Max 6 featured rooms
    
    def test_home_displays_building_names(self):
        """Buildings should appear in the home page"""
        Building.objects.create(name="NAC")
        Building.objects.create(name="Shepard Hall")
        
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        
        assert "NAC" in content
        assert "Shepard Hall" in content


@pytest.mark.django_db
class TestRoomListView:
    """Tests for the room_list view"""
    
    def test_room_list_returns_200(self):
        """The room list page should return a 200 status code"""
        client = Client()
        response = client.get("/rooms/")
        assert response.status_code == 200
    
    def test_room_list_uses_correct_template(self):
        """The room list view should use rooms/room_list.html"""
        client = Client()
        response = client.get("/rooms/")
        assert "rooms/room_list.html" in [t.name for t in response.templates]
    
    def test_room_list_displays_rooms(self):
        """Rooms in the database should appear in the response"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        response = client.get("/rooms/")
        content = response.content.decode()
        
        assert "NAC" in content
        assert "1/202" in content
        assert "30" in content
    
    def test_room_list_empty(self):
        """The page should still load when there are no rooms"""
        client = Client()
        response = client.get("/rooms/")
        assert response.status_code == 200
    
    def test_room_list_multiple_rooms(self):
        """Multiple rooms should all appear"""
        nac = Building.objects.create(name="NAC")
        shepard = Building.objects.create(name="Shepard Hall")
        
        Room.objects.create(building=nac, number="1/202", capacity=30)
        Room.objects.create(building=shepard, number="101", capacity=60)
        
        client = Client()
        response = client.get("/rooms/")
        content = response.content.decode()
        
        assert "NAC" in content
        assert "Shepard Hall" in content
    
    def test_room_list_filter_by_building(self):
        """Rooms can be filtered by building"""
        nac = Building.objects.create(name="NAC")
        shepard = Building.objects.create(name="Shepard Hall")
        
        Room.objects.create(building=nac, number="1/202", capacity=30)
        Room.objects.create(building=shepard, number="101", capacity=60)
        
        client = Client()
        response = client.get(f"/rooms/?building={nac.id}")
        
        assert response.context['rooms'].count() == 1
        assert response.context['rooms'].first().building == nac
    
    def test_room_list_filter_by_min_capacity(self):
        """Rooms can be filtered by minimum capacity"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        Room.objects.create(building=building, number="1/203", capacity=50)
        Room.objects.create(building=building, number="1/204", capacity=100)
        
        client = Client()
        response = client.get("/rooms/?min_capacity=50")
        
        assert response.context['rooms'].count() == 2
    
    def test_room_list_filter_invalid_min_capacity(self):
        """Invalid min_capacity should be ignored"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        response = client.get("/rooms/?min_capacity=invalid")
        
        # Should return all rooms when invalid
        assert response.context['rooms'].count() == 1
    
    def test_room_list_filter_empty_min_capacity(self):
        """Empty min_capacity should show all rooms"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        response = client.get("/rooms/?min_capacity=")
        
        assert response.context['rooms'].count() == 1
    
    def test_room_list_context_includes_buildings(self):
        """Context should include all buildings for filter dropdown"""
        Building.objects.create(name="NAC")
        Building.objects.create(name="Marshak")
        
        client = Client()
        response = client.get("/rooms/")
        
        assert 'buildings' in response.context
        assert response.context['buildings'].count() == 2


# =====================================================
# TESTS ON USER AUTHENTICATION
# =====================================================

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
    
    def test_register(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        })
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_password_mismatch(self):
        """Registration should fail if passwords don't match"""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'password1': 'strongpassword123',
            'password2': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_register_username_already_exists(self):
        """Registration should fail if username already exists"""
        response = self.client.post('/register/', {
            'username': 'testuser',  # Already exists
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
    
    def test_register_get_request(self):
        """GET request to register should show the form"""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_login(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_login_invalid_credentials(self):
        """Login should fail with wrong password"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page
    
    def test_login_nonexistent_user(self):
        """Login should fail for non-existent user"""
        response = self.client.post('/accounts/login/', {
            'username': 'nonexistent',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
    
    def test_logout_redirects_to_home(self):
        """Logout should redirect to home page"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post('/accounts/logout/')
        self.assertRedirects(response, '/')


# =====================================================
# TESTS ON FAVORITE ROOMS AND RESERVATIONS
# =====================================================

class RoomFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.building = Building.objects.create(name="NAC")
        self.room = Room.objects.create(building=self.building, number="101", capacity=30)
    
    def test_favorite_room(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/favorite/{self.room.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.room.favorites.filter(id=self.user.id).exists())
    
    def test_favorite_room_returns_json(self):
        """Favorite endpoint should return JSON response"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/favorite/{self.room.id}/')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['favorited'])
    
    def test_unfavorite_room(self):
        self.room.favorites.add(self.user)
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/favorite/{self.room.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.room.favorites.filter(id=self.user.id).exists())
    
    def test_unfavorite_room_returns_json(self):
        """Unfavorite should return JSON with favorited=false"""
        self.room.favorites.add(self.user)
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/favorite/{self.room.id}/')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(data['favorited'])
    
    def test_favorite_room_requires_login(self):
        """Favoriting without login should fail"""
        response = self.client.post(f'/favorite/{self.room.id}/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_favorite_nonexistent_room(self):
        """Favoriting non-existent room should return 404"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post('/favorite/99999/')
        self.assertEqual(response.status_code, 404)
    
    def test_favorite_room_get_request(self):
        """GET request to favorite endpoint should not be allowed"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(f'/favorite/{self.room.id}/')
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    def test_create_reservation(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post('/reserve/', {
            'room': self.room.id,
            'date': '2026-01-01',
            'start_time': '10:00',
            'end_time': '14:00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reservation.objects.filter(user=self.user).exists())
    
    def test_create_reservation_missing_fields(self):
        """Reservation should fail if required fields are missing"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post('/reserve/', {
            'room': self.room.id,
            # Missing date, time, duration
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Reservation.objects.filter(user=self.user).exists())
        self.assertIn('error', response.context)
    
    def test_create_reservation_requires_login(self):
        """Creating reservation without login should redirect"""
        response = self.client.post('/reserve/', {
            'room': self.room.id,
            'date': '2026-01-01',
            'start_time': '10:00',
            'end_time': '14:00'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_view_my_reservations(self):
        Reservation.objects.create(
            user=self.user,
            room=self.room,
            date='2026-01-01',
            start_time=time(10,0),
            end_time=time(14,0)
        )
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "101")  # room number
    
    def test_bookings_page_requires_login(self):
        """Bookings page should require login"""
        response = self.client.get('/bookings/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_bookings_page_empty(self):
        """Bookings page should handle no reservations"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no reservations")
    
    def test_favorite_rooms_page(self):
        """Favorite rooms page should show favorited rooms"""
        self.room.favorites.add(self.user)
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/favorites/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "101")
    
    def test_favorite_rooms_page_requires_login(self):
        """Favorites page should require login"""
        response = self.client.get('/favorites/')
        self.assertEqual(response.status_code, 302)
    
    def test_favorite_rooms_page_empty(self):
        """Favorites page should handle no favorites"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/favorites/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No favorite rooms")


# =====================================================
# SANITY TEST
# =====================================================

def test_sanity():
    """Basic sanity check that pytest is working"""
    assert True