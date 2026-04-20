"""
JSON API for reservations.

Endpoints:
  POST   /reservations/       — create request (pending)
  GET    /reservations/       — list current user's reservations
  PATCH  /reservations/<id>/  — staff: approve or reject
"""

import json
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rooms.models import Room

from .models import Reservation, has_approved_overlap


# ---------------------------------------------------------------------------
# Small helpers (single place for JSON shape and auth responses)
# ---------------------------------------------------------------------------


def _reservation_payload(r: Reservation) -> dict:
    return {
        "id": r.pk,
        "user_id": r.user_id,
        "room_id": r.room_id,
        "start_time": r.start_time.isoformat(),
        "end_time": r.end_time.isoformat(),
        "status": r.status,
    }


def _parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _require_user(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view(request, *args, **kwargs)

    return wrapped


def _require_staff(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"error": "Staff only"}, status=403)
        return view(request, *args, **kwargs)

    return wrapped


def _parse_datetimes(data):
    """Return (start, end) timezone-aware datetimes or (None, error_message)."""
    from django.utils.dateparse import parse_datetime

    raw_start = data.get("start_time")
    raw_end = data.get("end_time")
    if raw_start is None or raw_end is None:
        return None, "start_time and end_time are required"

    start = parse_datetime(str(raw_start))
    end = parse_datetime(str(raw_end))

    if start is None or end is None:
        return None, "Invalid start_time or end_time (use ISO 8601)"

    if end <= start:
        return None, "end_time must be after start_time"

    return (start, end), None


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


@csrf_exempt
@require_http_methods(["GET", "POST"])
@_require_user
def reservations_collection(request):
    if request.method == "GET":
        qs = Reservation.objects.filter(user=request.user).order_by("-start_time")
        return JsonResponse(
            {"reservations": [_reservation_payload(r) for r in qs]},
            status=200,
        )

    # POST — create pending request
    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    room_id = data.get("room_id")
    if room_id is None:
        return JsonResponse({"error": "room_id is required"}, status=400)

    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    (start, end), err = _parse_datetimes(data)
    if err:
        return JsonResponse({"error": err}, status=400)

    # Only approved reservations block new requests
    if has_approved_overlap(room, start, end):
        return JsonResponse(
            {"error": "Time conflict with an approved reservation"},
            status=409,
        )

    r = Reservation.objects.create(
        user=request.user,
        room=room,
        start_time=start,
        end_time=end,
        status=Reservation.Status.PENDING,
    )
    return JsonResponse(_reservation_payload(r), status=201)


@csrf_exempt
@require_http_methods(["PATCH"])
@_require_staff
def reservation_detail(request, reservation_id):
    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    new_status = data.get("status")
    if new_status not in (
        Reservation.Status.APPROVED,
        Reservation.Status.REJECTED,
    ):
        return JsonResponse(
            {"error": 'status must be "approved" or "rejected"'},
            status=400,
        )

    try:
        r = Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        return JsonResponse({"error": "Reservation not found"}, status=404)

    if new_status == Reservation.Status.APPROVED:
        if has_approved_overlap(r.room, r.start_time, r.end_time, exclude_reservation_id=r.pk):
            return JsonResponse(
                {"error": "Cannot approve: overlaps another approved reservation"},
                status=409,
            )

    r.status = new_status
    r.save(update_fields=["status"])
    return JsonResponse(_reservation_payload(r), status=200)
