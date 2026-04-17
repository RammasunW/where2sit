from django.db import models
from django.contrib.auth.models import User


class Building(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Room(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    capacity = models.IntegerField()
    favorites = models.ManyToManyField(User, related_name='favorite_rooms', blank=True)

    def __str__(self):
        return f"{self.building} - {self.number}"


# Reservation model for room booking
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    duration = models.PositiveIntegerField(help_text="Duration in hours")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Anonymous'} - {self.room} on {self.date} at {self.time}"

