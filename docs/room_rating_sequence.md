![Room Rating Feature Call Sequence](docs/room_rating_sequence.png)

### Room Rating Feature Call Sequence

The diagram above illustrates the call sequence for the room rating feature:
- The user opens the room detail page, which triggers a GET request to the Django server.
- The server queries the database for room details, ratings, and comments, then renders the page.
- When the user submits a rating, the browser sends a POST request to the server.
- The server creates or updates the RoomRating in the database and returns a JSON response.
- The frontend updates the UI to reflect the new rating.

This sequence ensures a smooth user experience and keeps the data consistent between the frontend and backend.