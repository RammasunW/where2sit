from django.contrib import admin
from .models import Room, Building, RoomIssueReport
# Register your models here.

admin.site.register(Room)
admin.site.register(Building)
admin.site.register(RoomIssueReport)