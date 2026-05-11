import pytest
from django.test import Client, TestCase
from django.contrib.auth.models import User
from rooms.models import Building, Room, Reservation, RoomRating, RoomIssueReport
from datetime import date, time
from django.urls import reverse
import json


# =====================================================
# VIEW + MODEL INTEGRATION TESTS
# =====================================================

@pytest.mark.django_db
class TestRoomListViewIntegration:
    """Integration tests for room_list view with database filtering"""
    
    def test_filter_rooms_by_building_integration(self):
        """View correctly filters rooms by building ID from database"""
        # Setup: Create buildings and rooms in database
        nac = Building.objects.create(name="NAC")
        shepard = Building.objects.create(name="Shepard Hall")
        marshak = Building.objects.create(name="Marshak")
        
        room1 = Room.objects.create(building=nac, number="1/202", capacity=30)
        room2 = Room.objects.create(building=nac, number="1/203", capacity=40)
        room3 = Room.objects.create(building=shepard, number="101", capacity=50)
        room4 = Room.objects.create(building=marshak, number="410", capacity=35)
        
        # Test: Filter by NAC
        client = Client()
        response = client.get(f'/rooms/?building={nac.id}')
        
        # Verify: Only NAC rooms returned
        assert response.status_code == 200
        rooms = response.context['rooms']
        assert rooms.count() == 2
        assert room1 in rooms
        assert room2 in rooms
        assert room3 not in rooms
        assert room4 not in rooms
    
    def test_filter_rooms_by_capacity_integration(self):
        """View correctly filters rooms by minimum capacity from database"""
        building = Building.objects.create(name="NAC")
        
        small_room = Room.objects.create(building=building, number="1/101", capacity=20)
        medium_room = Room.objects.create(building=building, number="1/202", capacity=40)
        large_room = Room.objects.create(building=building, number="1/303", capacity=100)
        
        client = Client()
        
        # Test: min_capacity=30 should exclude small_room
        response = client.get('/rooms/?min_capacity=30')
        rooms = response.context['rooms']
        
        assert rooms.count() == 2
        assert small_room not in rooms
        assert medium_room in rooms
        assert large_room in rooms
    
    def test_combined_filters_integration(self):
        """View correctly applies multiple filters simultaneously"""
        nac = Building.objects.create(name="NAC")
        shepard = Building.objects.create(name="Shepard Hall")
        
        # NAC rooms
        Room.objects.create(building=nac, number="1/101", capacity=20)
        nac_medium = Room.objects.create(building=nac, number="1/202", capacity=50)
        nac_large = Room.objects.create(building=nac, number="1/303", capacity=100)
        
        # Shepard rooms
        Room.objects.create(building=shepard, number="101", capacity=30)
        shepard_large = Room.objects.create(building=shepard, number="201", capacity=80)
        
        client = Client()
        
        # Test: NAC building + min_capacity=50
        response = client.get(f'/rooms/?building={nac.id}&min_capacity=50')
        rooms = response.context['rooms']
        
        assert rooms.count() == 2
        assert nac_medium in rooms
        assert nac_large in rooms
        assert shepard_large not in rooms
    
    def test_room_list_with_favorites_integration(self):
        """Room list displays favorite status correctly for logged-in users"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=40)
        
        # User favorites room1
        room1.favorites.add(user)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        response = client.get('/rooms/')
        
        content = response.content.decode()
        
        # Should show both rooms
        assert "1/202" in content
        assert "1/203" in content
        
        # Verify rooms are in context
        assert room1 in response.context['rooms']
        assert room2 in response.context['rooms']


@pytest.mark.django_db
class TestReservationViewIntegration:
    """Integration tests for reservation creation with database"""
    
    def test_create_reservation_full_flow(self):
        """Complete reservation flow: user login -> select room -> create reservation"""
        # Setup
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        
        # Step 1: Login
        login_success = client.login(username='testuser', password='pass123')
        assert login_success
        
        # Step 2: View reservation page
        response = client.get('/reserve/')
        assert response.status_code == 200
        assert room in response.context['rooms']
        
        # Step 3: Create reservation
        response = client.post('/reserve/', {
            'room': room.id,
            'date': '2026-05-15',
            'start_time': '10:00',
            'end_time': '12:00'
        })
        
        assert response.status_code == 200
        assert response.context['success'] is True
        
        # Step 4: Verify in database
        reservations = Reservation.objects.filter(user=user)
        assert reservations.count() == 1
        
        reservation = reservations.first()
        assert reservation.room == room
        assert reservation.date == date(2026, 5, 15)
        assert reservation.start_time == time(10, 0)
        assert reservation.end_time == time(12, 0)
    
    def test_create_multiple_reservations_same_user(self):
        """User can create multiple reservations across different rooms"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=40)
        room3 = Room.objects.create(building=building, number="1/204", capacity=50)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Create three reservations
        client.post('/reserve/', {
            'room': room1.id,
            'date': '2026-05-15',
            'start_time': '10:00',
            'end_time': '12:00'
        })
        
        client.post('/reserve/', {
            'room': room2.id,
            'date': '2026-05-16',
            'start_time': '14:00',
            'end_time': '15:00'
        })
        
        client.post('/reserve/', {
            'room': room3.id,
            'date': '2026-05-17',
            'start_time': '9:00',
            'end_time': '12:00'
        })
        
        # Verify all three exist
        assert Reservation.objects.filter(user=user).count() == 3
    
    def test_reservation_with_invalid_room_id(self):
        """Reservation fails with non-existent room"""
        user = User.objects.create_user(username='testuser', password='pass123')
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.post('/reserve/', {
            'room': 99999,  # Non-existent room
            'date': '2026-05-15',
            'start_time': '10:00',
            'end_time': '12:00'
        })
        
        # Should handle error and show error message
        assert response.status_code == 200
        assert 'error' in response.context
        assert response.context['error'] is not None
        assert 'does not exist' in response.context['error'].lower()
        
        # No reservation should be created
        assert Reservation.objects.filter(user=user).count() == 0
    
    def test_view_reservations_after_creation(self):
        """User can view their reservations after creating them"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Create reservation
        client.post('/reserve/', {
            'room': room.id,
            'date': '2026-05-15',
            'start_time': '10:00',
            'end_time': '12:00'
        })
        
        # View bookings page
        response = client.get('/bookings/')
        assert response.status_code == 200
        
        content = response.content.decode()
        assert "NAC" in content
        assert "1/202" in content
        # Django formats dates as "May 15, 2026" by default in templates
        assert "May 15, 2026" in content or "2026-05-15" in content
        assert "10 a.m." in content  # start time
        assert "noon" in content  # end time


@pytest.mark.django_db
class TestFavoriteToggleIntegration:
    """Integration tests for favorite toggle with database updates"""
    
    def test_favorite_toggle_updates_database(self):
        """Toggling favorite updates the many-to-many relationship in database"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Initially not favorited
        assert not room.favorites.filter(id=user.id).exists()
        
        # Toggle on
        response = client.post(f'/favorite/{room.id}/')
        assert response.status_code == 200
        
        # Verify in database
        room.refresh_from_db()
        assert room.favorites.filter(id=user.id).exists()
        
        # Verify response
        data = json.loads(response.content)
        assert data['favorited'] is True
        
        # Toggle off
        response = client.post(f'/favorite/{room.id}/')
        
        # Verify removed from database
        room.refresh_from_db()
        assert not room.favorites.filter(id=user.id).exists()
        
        data = json.loads(response.content)
        assert data['favorited'] is False
    
    def test_multiple_users_favorite_same_room(self):
        """Multiple users can favorite the same room independently"""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client1 = Client()
        client2 = Client()
        
        # User1 favorites
        client1.login(username='user1', password='pass123')
        client1.post(f'/favorite/{room.id}/')
        
        # User2 favorites
        client2.login(username='user2', password='pass123')
        client2.post(f'/favorite/{room.id}/')
        
        # Verify both in database
        room.refresh_from_db()
        assert room.favorites.filter(id=user1.id).exists()
        assert room.favorites.filter(id=user2.id).exists()
        assert room.favorites.count() == 2
        
        # User1 unfavorites
        client1.post(f'/favorite/{room.id}/')
        
        # User2's favorite should remain
        room.refresh_from_db()
        assert not room.favorites.filter(id=user1.id).exists()
        assert room.favorites.filter(id=user2.id).exists()
        assert room.favorites.count() == 1
    
    def test_view_favorites_after_favoriting(self):
        """Favorited rooms appear on favorites page"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=40)
        room3 = Room.objects.create(building=building, number="1/204", capacity=50)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Favorite room1 and room3
        client.post(f'/favorite/{room1.id}/')
        client.post(f'/favorite/{room3.id}/')
        
        # View favorites page
        response = client.get('/favorites/')
        assert response.status_code == 200
        
        # Verify context
        favorite_rooms = response.context['rooms']
        assert room1 in favorite_rooms
        assert room2 not in favorite_rooms
        assert room3 in favorite_rooms
        
        # Verify content
        content = response.content.decode()
        assert "1/202" in content
        assert "1/204" in content


# =====================================================
# AUTHENTICATION + VIEW INTEGRATION TESTS
# =====================================================

@pytest.mark.django_db
class TestAuthenticationFlowIntegration:
    """Integration tests for authentication flows"""
    
    def test_register_login_access_protected_view(self):
        """Complete flow: register -> login -> access protected view"""
        client = Client()
        
        # Step 1: Register
        response = client.post('/register/', {
            'username': 'newuser',
            'password1': 'strongpass123',
            'password2': 'strongpass123'
        })
        
        assert response.status_code == 302  # Redirect after registration
        assert User.objects.filter(username='newuser').exists()
        
        # Step 2: Should be auto-logged in after registration
        # Try to access protected view
        response = client.get('/reserve/')
        assert response.status_code == 200  # Accessible
    
    def test_logout_blocks_protected_views(self):
        """After logout, protected views should redirect to login"""
        user = User.objects.create_user(username='testuser', password='pass123')
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Can access while logged in
        response = client.get('/reserve/')
        assert response.status_code == 200
        
        # Logout
        client.post('/accounts/logout/')
        
        # Now should redirect
        response = client.get('/reserve/')
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_unauthorized_user_cannot_favorite(self):
        """Non-logged-in user cannot favorite rooms"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        
        # Try to favorite without login
        response = client.post(f'/favorite/{room.id}/')
        
        assert response.status_code == 302  # Redirect to login
        assert room.favorites.count() == 0  # No favorites added
    
    def test_user_only_sees_own_reservations(self):
        """Users can only see their own reservations, not others'"""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        # User1 makes a reservation
        Reservation.objects.create(
            user=user1,
            room=room,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        # User2 makes a reservation
        Reservation.objects.create(
            user=user2,
            room=room,
            date=date(2026, 5, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
        )
        
        client = Client()
        
        # Login as user1
        client.login(username='user1', password='pass123')
        response = client.get('/bookings/')
        
        # Should only see user1's reservation
        assert len(response.context['reservations']) == 1
        assert response.context['reservations'][0].user == user1


# =====================================================
# MULTI-MODEL INTEGRATION TESTS
# =====================================================

@pytest.mark.django_db
class TestMultiModelIntegration:
    """Integration tests involving multiple models working together"""
    
    def test_building_deletion_cascades_to_rooms_and_reservations(self):
        """Deleting a building cascades to rooms and their reservations"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=40)
        
        # Create reservations for both rooms
        Reservation.objects.create(
            user=user,
            room=room1,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        Reservation.objects.create(
            user=user,
            room=room2,
            date=date(2026, 5, 16),
            start_time=time(14, 0),
            end_time=time(15, 0),
        )
        
        # Verify setup
        assert Room.objects.count() == 2
        assert Reservation.objects.count() == 2
        
        # Delete building
        building.delete()
        
        # Verify cascade
        assert Building.objects.count() == 0
        assert Room.objects.count() == 0
        assert Reservation.objects.count() == 0
    
    def test_user_deletion_removes_reservations_but_not_rooms(self):
        """Deleting a user removes their reservations but leaves rooms intact"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        Reservation.objects.create(
            user=user,
            room=room,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        # Verify setup
        assert Reservation.objects.count() == 1
        assert Room.objects.count() == 1
        
        # Delete user
        user.delete()
        
        # Reservations gone, room remains
        assert Reservation.objects.count() == 0
        assert Room.objects.count() == 1
    
    def test_user_deletion_removes_favorites(self):
        """Deleting a user removes them from all favorite relationships"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        
        room1 = Room.objects.create(building=building, number="1/202", capacity=30)
        room2 = Room.objects.create(building=building, number="1/203", capacity=40)
        
        # User favorites both rooms
        room1.favorites.add(user)
        room2.favorites.add(user)
        
        assert room1.favorites.count() == 1
        assert room2.favorites.count() == 1
        
        # Delete user
        user.delete()
        
        # Favorites should be removed
        room1.refresh_from_db()
        room2.refresh_from_db()
        assert room1.favorites.count() == 0
        assert room2.favorites.count() == 0
    
    def test_room_with_reservations_and_favorites_deletion(self):
        """Deleting a room removes it from favorites and deletes reservations"""
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        # Two users favorite the room
        room.favorites.add(user1, user2)
        
        # User1 makes a reservation
        Reservation.objects.create(
            user=user1,
            room=room,
            date=date(2026, 5, 15),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        
        # Verify setup
        assert room.favorites.count() == 2
        assert Reservation.objects.count() == 1
        
        # Delete room
        room.delete()
        
        # Verify cleanup
        assert Room.objects.count() == 0
        assert Reservation.objects.count() == 0
        
        # Users still exist
        assert User.objects.filter(username='user1').exists()
        assert User.objects.filter(username='user2').exists()


# =====================================================
# EDGE CASE INTEGRATION TESTS
# =====================================================

@pytest.mark.django_db
class TestEdgeCaseIntegration:
    """Integration tests for edge cases and error conditions"""
    
    def test_filter_rooms_with_no_results(self):
        """Filtering rooms that don't exist returns empty queryset"""
        building = Building.objects.create(name="NAC")
        Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        
        # Filter by non-existent building
        response = client.get('/rooms/?building=99999')
        
        assert response.status_code == 200
        assert response.context['rooms'].count() == 0
    
    def test_reservation_page_with_no_rooms(self):
        """Reservation page works even when no rooms exist"""
        user = User.objects.create_user(username='testuser', password='pass123')
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.get('/reserve/')
        
        assert response.status_code == 200
        assert response.context['rooms'].count() == 0
    
    def test_concurrent_favorite_toggle(self):
        """Multiple rapid favorite toggles work correctly"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Toggle multiple times rapidly
        for i in range(5):
            response = client.post(f'/favorite/{room.id}/')
            data = json.loads(response.content)
            
            # Should alternate between favorited and unfavorited
            expected = (i % 2 == 0)  # True on even iterations
            assert data['favorited'] == expected
        
        # Final state should be favorited (5th toggle, index 4)
        room.refresh_from_db()
        assert room.favorites.filter(id=user.id).exists()
    
    def test_reservation_with_past_date(self):
        """System allows creating reservations with past dates (business logic decision)"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        # Try to create reservation with past date
        response = client.post('/reserve/', {
            'room': room.id,
            'date': '2020-01-01',  # Past date
            'start_time': '10:00',
            'end_time': '12:00',
        })
        
        # System currently allows this
        assert Reservation.objects.count() == 1
    
    def test_home_page_with_no_data(self):
        """Home page loads correctly with no buildings or rooms"""
        client = Client()
        response = client.get('/')
        
        assert response.status_code == 200
        assert response.context['buildings'].count() == 0
        
        # Check for either featured_rooms or top_rooms
        rooms_key = 'featured_rooms' if 'featured_rooms' in response.context else 'top_rooms'
        assert len(response.context[rooms_key]) == 0
    
    def test_empty_building_name_in_room_list(self):
        """Rooms with buildings that have empty names display correctly"""
        building = Building.objects.create(name="")
        Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        response = client.get('/rooms/')
        
        assert response.status_code == 200
        assert response.context['rooms'].count() == 1


# =====================================================
# ADDITIONAL RESERVATION ERROR HANDLING TESTS
# =====================================================

@pytest.mark.django_db
class TestReservationErrorHandling:
    """Test error handling in reservation creation"""
    
    def test_reservation_with_missing_room(self):
        """Reservation with missing room field should fail"""
        user = User.objects.create_user(username='testuser', password='pass123')
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.post('/reserve/', {
            # 'room': missing
            'date': '2026-05-15',
            'time': '10:00',
            'duration': 2
        })
        
        assert 'error' in response.context
        assert 'required' in response.context['error'].lower()
        assert Reservation.objects.count() == 0
    
    def test_reservation_with_missing_date(self):
        """Reservation with missing date should fail"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.post('/reserve/', {
            'room': room.id,
            # 'date': missing
            'time': '10:00',
            'duration': 2
        })
        
        assert 'error' in response.context
        assert Reservation.objects.count() == 0
    
    def test_reservation_with_missing_time(self):
        """Reservation with missing time should fail"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.post('/reserve/', {
            'room': room.id,
            'date': '2026-05-15',
            # 'time': missing
            'duration': 2
        })
        
        assert 'error' in response.context
        assert Reservation.objects.count() == 0
    
    def test_reservation_with_missing_duration(self):
        """Reservation with missing duration should fail"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.post('/reserve/', {
            'room': room.id,
            'date': '2026-05-15',
            'time': '10:00',
            # 'duration': missing
        })
        
        assert 'error' in response.context
        assert Reservation.objects.count() == 0
    
    def test_reservation_displays_in_context_immediately(self):
        """After creating reservation, it appears in the response context"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/202", capacity=30)
        
        client = Client()
        client.login(username='testuser', password='pass123')
        
        response = client.post('/reserve/', {
            'room': room.id,
            'date': '2026-05-15',
            'start_time': '10:00',
            'end_time': '12:00',
        })
        
        # The reservation view shows your reservations on the same page
        assert 'my_reservations' in response.context
        assert len(response.context['my_reservations']) == 1

# =====================================================
# TOGGLE FAVORITE ENDPOINT INTEGRATION TESTS
# (view + database)
# =====================================================
@pytest.mark.django_db
class TestToggleFavoriteIntegration:
    """Integration tests for toggle_favorite view interacting with the Room.favorites M2M field"""

    def test_toggle_favorite_adds_to_database(self):
        """POST to toggle_favorite adds the user to room.favorites in the database"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/100", capacity=30)

        client = Client()
        client.login(username='testuser', password='pass123')

        assert not room.favorites.filter(id=user.id).exists()

        response = client.post(f'/favorite/{room.id}/')
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is True
        assert data['favorited'] is True

        room.refresh_from_db()
        assert room.favorites.filter(id=user.id).exists()

    def test_toggle_favorite_removes_from_database(self):
        """POST to toggle_favorite a second time removes the user from room.favorites"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/100", capacity=30)
        room.favorites.add(user)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(f'/favorite/{room.id}/')
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is True
        assert data['favorited'] is False

        room.refresh_from_db()
        assert not room.favorites.filter(id=user.id).exists()

    def test_toggle_favorite_unauthenticated_does_not_modify_database(self):
        """Unauthenticated POST to toggle_favorite is redirected and database is unchanged"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="1/100", capacity=30)

        client = Client()
        response = client.post(f'/favorite/{room.id}/')

        assert response.status_code == 302
        assert '/accounts/login/' in response.url
        assert room.favorites.count() == 0


# =====================================================
# RATE ROOM ENDPOINT INTEGRATION TESTS
# (view + RoomRating creation)
# =====================================================
@pytest.mark.django_db
class TestRateRoomIntegration:
    """Integration tests for rate_room view interacting with the RoomRating model"""

    def test_rate_room_creates_rating_in_database(self):
        """POST to rate_room creates a RoomRating record linked to the correct user and room"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="2/200", capacity=40)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/rate/',
            {'score': '4', 'comment': 'Pretty good room.'}
        )
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is True

        rating = RoomRating.objects.get(user=user, room=room)
        assert rating.score == 4
        assert rating.comment == 'Pretty good room.'

    def test_rate_room_updates_existing_rating(self):
        """POST to rate_room a second time updates the existing RoomRating rather than creating a duplicate"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="2/200", capacity=40)
        RoomRating.objects.create(user=user, room=room, score=2, comment='Meh.')

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/rate/',
            {'score': '5', 'comment': 'Changed my mind, great room!'}
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        # Only one rating should exist
        assert RoomRating.objects.filter(user=user, room=room).count() == 1
        rating = RoomRating.objects.get(user=user, room=room)
        assert rating.score == 5
        assert rating.comment == 'Changed my mind, great room!'

    def test_rate_room_missing_score_returns_error(self):
        """POST to rate_room without a score returns success=False and creates no RoomRating"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="2/200", capacity=40)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(f'/rooms/{room.id}/rate/', {'comment': 'No score provided.'})
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is False
        assert 'error' in data
        assert RoomRating.objects.filter(user=user, room=room).count() == 0


# =====================================================
# REPORT ROOM ISSUE ENDPOINT INTEGRATION TESTS
# (view + RoomIssueReport creation)
# =====================================================
@pytest.mark.django_db
class TestReportRoomIssueIntegration:
    """Integration tests for report_room_issue view interacting with RoomIssueReport model"""

    def test_report_room_issue_creates_record_in_database(self):
        """Valid POST to report_room_issue creates a RoomIssueReport in the database"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="3/300", capacity=25)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/report-issue/',
            {'description': 'The projector is broken and will not turn on.'}
        )
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is True

        report = RoomIssueReport.objects.get(user=user, room=room)
        assert report.description == 'The projector is broken and will not turn on.'
        assert report.status == RoomIssueReport.Status.OPEN

    def test_report_room_issue_description_too_short_returns_error(self):
        """POST with a description shorter than 5 characters returns an error and creates no report"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="3/300", capacity=25)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/report-issue/',
            {'description': 'Bad'}
        )
        assert response.status_code == 400

        data = json.loads(response.content)
        assert data['success'] is False
        assert 'error' in data
        assert RoomIssueReport.objects.filter(user=user, room=room).count() == 0

    def test_report_room_issue_unauthenticated_is_redirected(self):
        """Unauthenticated POST to report_room_issue redirects to login and creates no report"""
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="3/300", capacity=25)

        client = Client()
        response = client.post(
            f'/rooms/{room.id}/report-issue/',
            {'description': 'The air conditioning is not working at all.'}
        )

        assert response.status_code == 302
        assert '/accounts/login/' in response.url
        assert RoomIssueReport.objects.count() == 0


# =====================================================
# ROOM RESERVE ENDPOINT INTEGRATION TESTS
# (view + availability checking)
# =====================================================
@pytest.mark.django_db
class TestRoomReserveIntegration:
    """Integration tests for room_reserve view with Room.is_available availability checking"""

    def test_room_reserve_creates_reservation_when_available(self):
        """POST to room_reserve creates a Reservation when the room has no conflicts"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="4/400", capacity=30)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/reserve/',
            {'date': '2027-06-01', 'start_time': '10:00', 'end_time': '12:00'}
        )
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is True

        reservation = Reservation.objects.get(user=user, room=room)
        assert str(reservation.date) == '2027-06-01'

    def test_room_reserve_fails_when_conflicting_reservation_exists(self):
        """POST to room_reserve returns an error when an existing reservation overlaps the requested time"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="4/400", capacity=30)

        # Create a blocking reservation
        Reservation.objects.create(
            user=user,
            room=room,
            date='2027-06-01',
            start_time='09:00',
            end_time='11:00',
        )

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/reserve/',
            {'date': '2027-06-01', 'start_time': '10:00', 'end_time': '12:00'}
        )
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is False
        assert 'not available' in data['error'].lower()

        # Only the original reservation should exist
        assert Reservation.objects.filter(room=room).count() == 1

    def test_room_reserve_fails_when_end_time_before_start_time(self):
        """POST to room_reserve with end_time <= start_time returns an error"""
        user = User.objects.create_user(username='testuser', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="4/400", capacity=30)

        client = Client()
        client.login(username='testuser', password='pass123')

        response = client.post(
            f'/rooms/{room.id}/reserve/',
            {'date': '2027-06-01', 'start_time': '14:00', 'end_time': '10:00'}
        )
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['success'] is False
        assert Reservation.objects.filter(user=user, room=room).count() == 0


# =====================================================
# MANAGER RESERVATION APPROVAL WORKFLOW INTEGRATION TESTS
# (view + Reservation status update)
# =====================================================
@pytest.mark.django_db
class TestManagerReservationApprovalIntegration:
    """Integration tests for the manager reservation approval workflow"""

    def _make_manager(self, username='manager', password='pass123'):
        from django.contrib.auth.models import Group
        user = User.objects.create_user(username=username, password=password)
        group, _ = Group.objects.get_or_create(name='Manager')
        user.groups.add(group)
        return user

    def test_manager_can_approve_pending_reservation(self):
        """A manager POST to update_reservation_status with Approved changes the reservation status"""
        manager = self._make_manager()
        regular_user = User.objects.create_user(username='student', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="5/500", capacity=50)
        reservation = Reservation.objects.create(
            user=regular_user,
            room=room,
            date='2027-07-10',
            start_time='09:00',
            end_time='11:00',
            status='Pending',
        )

        client = Client()
        client.login(username='manager', password='pass123')

        response = client.post(
            f'/manage_reservations/{reservation.id}/update_status/',
            {'status': 'Approved'}
        )
        # Should redirect back to manage_reservations
        assert response.status_code == 302

        reservation.refresh_from_db()
        assert reservation.status == 'Approved'

    def test_manager_can_reject_pending_reservation(self):
        """A manager POST to update_reservation_status with Rejected changes the reservation status"""
        manager = self._make_manager()
        regular_user = User.objects.create_user(username='student', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="5/500", capacity=50)
        reservation = Reservation.objects.create(
            user=regular_user,
            room=room,
            date='2027-07-10',
            start_time='09:00',
            end_time='11:00',
            status='Pending',
        )

        client = Client()
        client.login(username='manager', password='pass123')

        response = client.post(
            f'/manage_reservations/{reservation.id}/update_status/',
            {'status': 'Rejected'}
        )
        assert response.status_code == 302

        reservation.refresh_from_db()
        assert reservation.status == 'Rejected'

    def test_non_manager_cannot_update_reservation_status(self):
        """A regular user POST to update_reservation_status receives a 403 and status is unchanged"""
        regular_user = User.objects.create_user(username='student', password='pass123')
        building = Building.objects.create(name="NAC")
        room = Room.objects.create(building=building, number="5/500", capacity=50)
        reservation = Reservation.objects.create(
            user=regular_user,
            room=room,
            date='2027-07-10',
            start_time='09:00',
            end_time='11:00',
            status='Pending',
        )

        client = Client()
        client.login(username='student', password='pass123')

        response = client.post(
            f'/manage_reservations/{reservation.id}/update_status/',
            {'status': 'Approved'}
        )
        assert response.status_code == 403

        reservation.refresh_from_db()
        assert reservation.status == 'Pending'