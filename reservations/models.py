from django.db import models
from django.contrib.auth.models import User

class Building(models.Model):
    name = models.CharField(max_length=100)

class Room(models.Model):
    name = models.CharField(max_length=100)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user} - {self.room} ({self.start_time} to {self.end_time})"
def is_conflict(room, start, end):
    return Reservation.objects.filter(
        room=room,
        start_time__lt=end,
        end_time__gt=start
    ).exists()