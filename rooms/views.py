from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Room, Building
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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

    building = request.GET.get("building")
    min_capacity = request.GET.get("min_capacity")

    if building:
        try:
            rooms = rooms.filter(building__name=building)
        except ValueError:
            pass

    if min_capacity:
        try:
            rooms = rooms.filter(capacity__gte=int(min_capacity))
        except ValueError:
            pass

    return render(request, "rooms/room_list.html", context)


# User authentication

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# Reservation view (no login required)

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import redirect
from .models import Reservation


@login_required
def reservation(request):
    rooms = Room.objects.select_related('building').all()
    success = False
    error = None

    if request.method == 'POST':
        room_id = request.POST.get('room')
        date = request.POST.get('date')
        time_ = request.POST.get('time')
        duration = request.POST.get('duration')
        if not (room_id and date and time_ and duration):
            error = 'Please fill in all required fields.'
        else:
            try:
                reservation = Reservation.objects.create(
                    user=request.user,
                    room_id=room_id,
                    date=date,
                    time=time_,
                    duration=duration,
                )
                success = True
            except Exception as e:
                error = f"Reservation failed: {e}"

    my_reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'rooms': rooms,
        'success': success,
        'error': error,
        'my_reservations': my_reservations,
    }
    return render(request, "rooms/reservation.html", context)


# View reservations
@login_required
def bookings(request):
    reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, "rooms/bookings.html", {
        "reservations": reservations
    })


# Favorite rooms
@login_required
def favorite_rooms(request):
    rooms = request.user.favorite_rooms.all()
    return render(request, "rooms/favorites.html", {"rooms": rooms})


@login_required
@require_POST
def toggle_favorite(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.user in room.favorites.all():
        room.favorites.remove(request.user)
        is_favorited = False
    else:
        room.favorites.add(request.user)
        is_favorited = True

    return JsonResponse({
        'success': True,
        'favorited': is_favorited
    })

