-- Reservation tables (Django app `reservations`). Rooms are defined in `rooms`.
--
-- reservations_reservation
--   user_id     -> django.contrib.auth User
--   room_id     -> rooms.Room
--   start_time, end_time  (timezone-aware in Django)
--   status      'pending' | 'approved' | 'rejected'
--
-- Business rule: only rows with status = 'approved' block overlapping bookings.

CREATE TABLE IF NOT EXISTS reservations_reservation (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED,
    room_id     INTEGER NOT NULL REFERENCES rooms_room (id) ON DELETE CASCADE,
    start_time  DATETIME NOT NULL,
    end_time    DATETIME NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
);
