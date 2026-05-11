from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg
from .models import Room, Building, RoomRating, Reservation
from datetime import datetime, date
# Create your views here.

def home(request):
    buildings = Building.objects.all()
    rooms = Room.objects.annotate(
        avg_rating=Avg('ratings__score')
    ).order_by('-avg_rating')[:5]

    now = datetime.now()
    date_now = now.date().isoformat(),
    time_now = now.strftime("%H:%M"),

    context = {
        'buildings': buildings,
        'date_now': date_now[0],
        'time_now': time_now[0],
        'top_rooms': rooms,
    }
    return render(request, "rooms/home.html", context)

def room_list(request):
    rooms = Room.objects.select_related('building').annotate(avg_rating=Avg('ratings__score'))
    buildings = Building.objects.all()

    building_id = request.GET.get('building')
    date = request.GET.get('date')
    time = request.GET.get('time')
    min_capacity = request.GET.get('min_capacity')
    min_rating = request.GET.get('min_rating')

    if building_id:
        rooms = rooms.filter(building_id=building_id)
    
    if min_capacity and min_capacity != '':
        try:
            min_capacity = int(min_capacity)
            rooms = rooms.filter(capacity__gte=min_capacity)
        except ValueError:
            pass

    if min_rating and min_rating != '':
        try:
            min_rating_val = float(min_rating)
            rooms = rooms.filter(avg_rating__gte=min_rating_val)
        except ValueError:
            pass

    if date and time:
        date_ = datetime.strptime(date, "%Y-%m-%d").date()
        start_time = datetime.strptime(time, "%H:%M").time()
        rooms = [room for room in rooms if room.is_available(date_, start_time, start_time)]

    selected_building = building_id if building_id else ''
    selected_date = date if date else ''
    selected_time = time if time else ''
    selected_min_rating = min_rating if min_rating else ''

    context = {
        'rooms': rooms,
        'buildings': buildings,
        'selected_building': selected_building,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'min_capacity': min_capacity,
        'selected_min_rating': selected_min_rating,
    }

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
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not (room_id and date and start_time and end_time):
            error = 'Please fill in all required fields.'
        else:
            date_ = datetime.strptime(date, "%Y-%m-%d").date()
            start_time_ = datetime.strptime(start_time, "%H:%M").time()
            end_time_ = datetime.strptime(end_time, "%H:%M").time()

            if start_time_ > end_time_:
                error = 'Please fill in the correct time.'
            else:
                try:
                    # Validate room exists
                    room = Room.objects.get(id=room_id)

                    if not room.is_available(date_, start_time_, end_time_):
                        error = "Room is not available at this time."
                    
                    # cannot have more than 5 active reservations
                    elif Reservation.objects.filter(user=request.user, date__gte=timezone.now().date(), status__in=['Pending', 'Approved']).count() >= 5:
                        error = "You cannot have more than 5 active reservations."

                    else:
                        reservation = Reservation.objects.create(
                            user=request.user,
                            room=room,  # Use the room object instead of room_id
                            date=date,
                            start_time=start_time,
                            end_time=end_time,
                        )
                        success = True
                except Room.DoesNotExist:
                    error = 'The selected room does not exist.'
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
        user=request.user,
        status__in=['Pending', 'Approved'],
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

@require_POST
@login_required
def rate_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        score = request.POST.get("score")
        comment = request.POST.get("comment", "")

        if not score:
            return JsonResponse({"success": False, "error": "Score is required"})

        rating, created = RoomRating.objects.get_or_create(
            user=request.user,
            room=room,
            defaults={
                "score": int(score),
                "comment": comment
            }
        )
        if not created:
            rating.score = int(score)
            rating.comment = comment
            rating.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"})

def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    ratings = room.ratings.select_related('user').order_by('-created_at')
    date_str = request.GET.get('date')

    # Show room availability by date, default to today
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = date.today()

    schedule = room.get_schedule_for_day(selected_date)

    context = {
        'room': room,
        'average_rating': room.average_rating,
        'rating_count': room.rating_count,
        'ratings': ratings,
        'schedule': schedule,
        'selected_date': selected_date,
    }
    return render(request, 'rooms/room_detail.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def room_reserve(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    date_str = request.POST.get('date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    if not (date_str and start_time and end_time):
        return JsonResponse({'success': False, 'error': 'Please fill in all required fields.'})
    try:
        date_ = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time_ = datetime.strptime(start_time, "%H:%M").time()
        end_time_ = datetime.strptime(end_time, "%H:%M").time()
        if start_time_ >= end_time_:
            return JsonResponse({'success': False, 'error': 'End time must be after start time.'})
        if not room.is_available(date_, start_time_, end_time_):
            return JsonResponse({'success': False, 'error': 'Room is not available at this time.'})
        Reservation.objects.create(
            user=request.user,
            room=room,
            date=date_,
            start_time=start_time_,
            end_time=end_time_,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def home(request):
    rooms = Room.objects.annotate(
        avg_rating=Avg('ratings__score')
    ).order_by('-avg_rating')[:5]
    
    buildings = Building.objects.all()

    context = {
        'top_rooms': rooms,
        'buildings': buildings,
    }
    return render(request, 'rooms/home.html', context)

def manage_reservations(request):
    
    context = {
        'reservations': Reservation.objects.filter(status='Pending').order_by('-created_at')
    }
    
    return render(request, 'rooms/manage_reservations.html', context)

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

@login_required
def update_reservation_status(request, reservation_id):
    new_status = request.POST.get('status')
    if not is_manager(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    reservation = get_object_or_404(Reservation, id=reservation_id)

    if new_status not in ['Approved', 'Rejected']:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

    reservation.status = new_status
    reservation.save()
    
    if new_status == 'Approved':
        messages.success(
            request,
            f"{reservation.user.username}'s reservation for {reservation.room} on {reservation.date} has been approved."
        )
    else:
        messages.error(
            request,
            f"{reservation.user.username}'s reservation for {reservation.room} for {reservation.date} has been rejected."
        )

    return redirect('rooms:manage_reservations')
