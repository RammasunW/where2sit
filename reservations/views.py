from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.contrib.auth.models import User

from .models import Reservation, Room

@csrf_exempt
def create_reservation(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.first()
        room = Room.objects.get(id=data["room_id"])

        start = datetime.fromisoformat(data["start_time"])
        end = datetime.fromisoformat(data["end_time"])

        if is_conflict(room, start, end):
            return JsonResponse({"error": "Time conflict"}, status=400)

        Reservation.objects.create(
            user=user,
            room=room,
            start_time=start,
            end_time=end
        )

        return JsonResponse({"message": "Reservation successful"})

    # ❗ 关键：处理 GET 请求
    return JsonResponse({"error": "Only POST allowed"}, status=405)