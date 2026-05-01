from django.urls import path

from . import views

urlpatterns = [
    path("reservations/", views.reservations_collection),
    path("reservations/<int:reservation_id>/", views.reservation_detail),
]
