from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path("", views.home, name="home"),
    #path("", views.room_list, name="room_list"),
    path('rooms/', views.room_list, name="room_list"),
    path('reserve/', views.reservation, name="reservation"),
    path('register/', views.register, name='register'),
    path('bookings/', views.bookings, name='bookings'),
    path('favorite/<int:room_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_rooms, name='favorites'),
]