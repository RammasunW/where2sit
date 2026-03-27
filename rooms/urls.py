from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path("", views.home, name="home"),
    #path("", views.room_list, name="room_list"),
    path('rooms/', views.room_list, name="room_list"),
]