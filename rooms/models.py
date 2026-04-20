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
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 2)
        return None

    @property
    def rating_count(self):
        return self.ratings.count()

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


class RoomRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='ratings', on_delete=models.CASCADE)
    score = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Move unique_together into the constraints list
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'room'], 
                name='unique_user_room_rating'
            ),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.room} ({self.score})"