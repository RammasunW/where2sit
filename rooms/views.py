from django.shortcuts import render
from .models import Room, Building

# Create your views here.

def home(request):
    featured_rooms = Room.objects.select_related('building').all()[:6]
    buildings = Building.objects.all()

    context = {
        'featured_rooms': featured_rooms,
        'buildings': buildings,
    }
    return render(request, "rooms/home.html", context)

def room_list(request):
    rooms = Room.objects.all()
    buildings = Building.objects.all()

    building_id = request.GET.get('building') # consider using id instead of name
    date = request.GET.get('date')
    time = request.GET.get('time')
    min_capacity = request.GET.get('min_capacity')

    if building_id:
        rooms = rooms.filter(building_id=building_id)
    
    if min_capacity and min_capacity != '':
        try:
            min_capacity = int(min_capacity)
            rooms = rooms.filter(capacity__gte=min_capacity)
        except ValueError:
            pass

    selected_building = building_id if building_id else ''
    selected_date = date if date else ''
    selected_time = time if time else ''
    
    context = {
        'rooms': rooms,
        'buildings': buildings,
        'selected_building': selected_building,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'min_capacity': min_capacity,
    }

    return render(request, "rooms/room_list.html", context)
