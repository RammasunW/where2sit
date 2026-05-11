from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path("", views.home, name="home"),
    path('rooms/', views.room_list, name="room_list"),
    path('reserve/', views.reservation, name="reservation"),
    path('register/', views.register, name='register'),
    path('bookings/', views.bookings, name='bookings'),
    path('favorite/<int:room_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_rooms, name='favorites'),
    path('rooms/<int:room_id>/rate/', views.rate_room, name='rate_room'),
    path('rooms/<int:room_id>/reserve/', views.room_reserve, name='room_reserve'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('manage_reservations/', views.manage_reservations, name='manage_reservations'),
    path('manage_reservations/<int:reservation_id>/update_status/', views.update_reservation_status, name='update_reservation_status'),
    path('manage_issues/', views.manage_room_issues, name='manage_room_issues'),
    path('manage_issues/<int:report_id>/resolve/', views.resolve_room_issue, name='resolve_room_issue'),
    path('rooms/<int:room_id>/report-issue/', views.report_room_issue, name='report_room_issue'),

    path('manage/rooms/', views.manage_rooms, name='manage_rooms'),
    path('manage/rooms/add/', views.add_room, name='add_room'),
    path('manage/rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('manage/rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),

    path('manage/classes/', views.manage_classes, name='manage_classes'),
    path('manage/classes/add/', views.add_class, name='add_class'),
    path('manage/classes/<int:class_id>/edit/', views.edit_class, name='edit_class'),
    path('manage/classes/<int:class_id>/delete/', views.delete_class, name='delete_class'),

    path('', views.home, name='home'),
]