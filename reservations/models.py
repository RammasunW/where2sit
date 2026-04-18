"""
Reservation domain (single source of truth for rooms: see rooms.models.Room).

Schema (PostgreSQL/SQLite via Django ORM):

  reservations_reservation
    id            BIGSERIAL PRIMARY KEY
    user_id       FK -> auth_user (CASCADE)
    room_id       FK -> rooms_room (CASCADE)
    start_time    TIMESTAMPTZ NOT NULL
    end_time      TIMESTAMPTZ NOT NULL
    status        VARCHAR(20) NOT NULL  -- pending | approved | rejected

  -- Only rows with status = 'approved' participate in overlap checks for availability.
"""

from django.conf import settings
from django.db import models

from rooms.models import Room


class Reservation(models.Model):
    """A user's request to book a room for [start_time, end_time)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    # user_id in API terms — Django uses FK
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    def __str__(self):
        return f"{self.user_id} room={self.room_id} {self.start_time}–{self.end_time} [{self.status}]"


def has_approved_overlap(room, start, end, exclude_reservation_id=None):
    """
    True if an APPROVED reservation overlaps [start, end).
    Standard overlap: (start_a < end_b) and (end_a > start_b).
    """
    qs = Reservation.objects.filter(
        room=room,
        status=Reservation.Status.APPROVED,
        start_time__lt=end,
        end_time__gt=start,
    )
    if exclude_reservation_id is not None:
        qs = qs.exclude(pk=exclude_reservation_id)
    return qs.exists()
