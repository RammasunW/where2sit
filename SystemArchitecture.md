# Where2sit Architecture

## 1. High-Level Component Diagram
```mermaid
graph TB
    User[Web Browser/User]
    
    subgraph "Django Application"
        Django[Django Web Server]
        Views[Views Layer<br/>rooms/views.py]
        Models[Models Layer<br/>Building, Room, Reservation, RoomRating]
        Auth[Django Auth System]
        Static[Static Files<br/>TailwindCSS]
    end
    
    DB[(SQLite Database<br/>db.sqlite3)]
    
    User -->|HTTP/HTTPS| Django
    Django --> Views
    Views --> Models
    Views --> Auth
    Models --> DB
    Auth --> DB
    Django --> Static
    Static --> User
```
The where2sit application follows a traditional Django MVC architecture. Users interact with the
system through a web browser, sending HTTP requests to the Django web server. The Views layer
handles incoming requests and coordinates between the Models layer and templates. The Models layer
consists of four main entities: Building, Room, Reservation, and RoomRating, which interact with
the SQLite database. Django's built-in authentication system manages user login, registration,
and session management. Static files (primarily TailwindCSS) are served to provide the user interface
styling. All database interactions flow through Django's ORM, ensuring data consistency and security.

## 2. Entity Relationship Diagram
```mermaid
erDiagram
    User ||--o{ Reservation : creates
    User }o--o{ Room : favorites
    Room ||--o{ Reservation : "is reserved"
    Building ||--o{ Room : contains
    Room ||--o{ RoomRating : "has ratings"
    User ||--o{ RoomRating : writes
    
    User {
        int id PK
        string username
        string password
        datetime date_joined
    }
    
    Building {
        int id PK
        string name
    }
    
    Room {
        int id PK
        int building_id FK
        string number
        int capacity
    }
    
    Reservation {
        int id PK
        int user_id FK
        int room_id FK
        string name
        date date
        time time
        int duration
        datetime created_at
    }
    
    RoomRating {
        int id PK
        int user_id FK
        int room_id FK
        int score
        text comment
        datetime created_at
    }
```
The reservation system's data model centers around five main entities. A Building contains multiple
Rooms (one-to-many relationship). Users can create multiple Reservations for different Rooms
(many-to-one relationships). The system also supports a many-to-many relationship between Users and
Rooms through the favorites feature, allowing users to mark their preferred study spaces. Users can
write RoomRatings for Rooms they've used, establishing another many-to-one relationship. When a
Building is deleted, all associated Rooms are cascade-deleted, which in turn deletes all Reservations
and RoomRatings for those rooms. Similarly, when a User is deleted, their Reservations and RoomRatings
are removed, but the Rooms themselves remain intact.

## 3. Sequence Diagram
```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Django
    participant View as reservation()<br/>view
    participant Auth as @login_required
    participant Room as Room Model
    participant Reservation as Reservation Model
    participant DB as Database
    
    User->>Browser: Click "Reservation" link
    Browser->>Django: GET /reserve/
    Django->>Auth: Check authentication
    
    alt Not authenticated
        Auth-->>Browser: Redirect to /accounts/login/
        Browser-->>User: Show login page
    else Authenticated
        Auth->>View: Allow access
        View->>Room: Room.objects.all()
        Room->>DB: SELECT * FROM rooms
        DB-->>Room: Room data
        Room-->>View: List of rooms
        View-->>Browser: Render reservation.html with rooms
        Browser-->>User: Display reservation form
        
        User->>Browser: Fill form & submit
        Browser->>Django: POST /reserve/<br/>(room, date, time, duration)
        Django->>View: Handle POST request
        View->>Room: Room.objects.get(id=room_id)
        Room->>DB: SELECT room WHERE id=?
        DB-->>Room: Room object
        Room-->>View: Room exists
        View->>Reservation: Reservation.objects.create()
        Reservation->>DB: INSERT INTO reservations
        DB-->>Reservation: Success
        Reservation-->>View: Reservation created
        View->>Reservation: Get user's reservations
        Reservation->>DB: SELECT WHERE user_id=?
        DB-->>Reservation: User's reservations
        Reservation-->>View: Reservation list
        View-->>Browser: Render with success message
        Browser-->>User: Show confirmation & reservations
    end
```
The room reservation flow begins when an authenticated user navigates to the reservation page. The
@login_required decorator checks authentication status; unauthenticated users are redirected to
login. Once authenticated, the view retrieves all available rooms from the database via the Room
model and renders the reservation form. When the user submits the form with room selection, date,
time, and duration, a POST request is sent to the server. The view validates that the selected room
exists by querying the database, then creates a new Reservation object linking the user to the room
with the specified time details. After successful creation, the view queries the user's reservations
to display them on the same page, providing immediate feedback. If any error occurs (such as an invalid
room ID or missing fields), the view catches the exception and displays an error message without
creating the reservation.
