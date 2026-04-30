Hotel Reservation Management System

The Hotel Reservation Management System is a full-stack Flask web application designed for hotel administrators. The application allows an admin user to manage guests, rooms, room types, and reservations through a browser-based interface connected to a local MySQL database.

The system uses a normalized relational database structure and supports common hotel management tasks such as adding guests, updating room information, creating reservations, viewing reservation details, and displaying dashboard summaries. The project demonstrates database normalization, multi-table CRUD operations, relationship management, server-side validation, transaction logic, and SQL aggregate queries.

Technology Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- MySQL
- PyMySQL
- python-dotenv
- HTML5
- CSS3
- Bootstrap 5
- Jinja2 Templates
- Git / GitHub

Project Features

Dashboard
The dashboard displays high-level information about the hotel database.
The dashboard uses SQL aggregate functions such as `COUNT`, `SUM`, and `AVG`.

Guest Management
- View all guests
- Add a new guest
- Edit an existing guest
- Delete a guest if they do not have reservations
- View guest details
- View all reservations belonging to a guest
This demonstrates a one-to-many relationship between guests and reservations.

Room Management
- View all rooms
- Add a new room
- Edit an existing room
- Delete a room if it does not have reservations
- View room details
- View all reservations for a room
Rooms are connected to room types and room statuses through foreign keys.

Room Type Management
- View all room types
- Add a new room type
- Edit an existing room type
- Delete a room type if no rooms are using it
Room types store information such as type name, maximum occupancy, and base price.

Reservation Management
- View all reservations
- Add a new reservation
- Edit an existing reservation
- Delete a reservation
- View reservation details

When a reservation is created, the application validates the input, checks for overlapping reservations, inserts the reservation, and updates the related room status in a single transaction.

Server-Side Validation
The application includes backend validation to help prevent bad data from entering the database. Examples include:
- Guest first name and last name cannot be empty
- Guest email must be unique if provided
- Room number cannot be empty
- Room number must be unique
- Room type must exist
- Room status must exist
- Base price cannot be negative
- Max occupancy must be greater than zero
- Check-out date must be after check-in date
- Reservations cannot overlap for the same room

Transaction Logic
The reservation creation feature uses transaction logic. When a reservation is created, the application performs multiple related database actions:
1. Validate the guest, room, employee, and dates.
2. Check that the room is not already booked for overlapping dates.
3. Insert the new reservation.
4. Update the room status to Reserved.
5. Commit both changes together.
If any part fails, the transaction is rolled back.

Database Design
The final database is normalized to Third Normal Form and includes the following main tables:
- RoomTypes
- RoomStatuses
- Rooms
- Guests
- Employees
- Reservations
The database also includes a ReservationDetails view. This view joins reservation, guest, room, room type, and employee data together for easier display in the application.

The normalization process is documented in Normalization.md.

Project Structure

    Project_3_CS665/
    ├── app.py
    ├── config.py
    ├── models.py
    ├── requirements.txt
    ├── README.md
    ├── Normalization.md
    ├── AI_LOG.md
    ├── .gitignore
    ├── SQL/
    │   ├── Schema.sql
    │   └── Seed.sql
    ├── static/
    │   └── css/
    │       └── styles.css
    └── templates/
        ├── base.html
        ├── dashboard.html
        ├── guests/
        │   ├── list.html
        │   ├── form.html
        │   └── detail.html
        ├── rooms/
        │   ├── list.html
        │   ├── form.html
        │   └── detail.html
        ├── room_types/
        │   ├── list.html
        │   └── form.html
        └── reservations/
            ├── list.html
            ├── form.html
            └── detail.html

Installation Instructions

1. Clone the Repository

    git clone https://github.com/EthanZ3/Project_3_CS665.git
    cd Project_3_CS665

2. Create a Virtual Environment

    python -m venv venv

3. Activate the Virtual Environment

On Windows:

    venv\Scripts\activate

4. Install Required Packages

    pip install -r requirements.txt

Environment Setup

Create a .env file in the root of the project folder.

Example .env file:

    DB_USER=root
    DB_PASSWORD=your_mysql_password
    DB_HOST=localhost
    DB_PORT=3306
    DB_NAME=hotel_reservation_db
    SECRET_KEY=dev-secret-key

Replace `your_mysql_password` with the password for your local MySQL user.

Database Setup

This project uses a local MySQL database.

1. Open MySQL or a MySQL Extension in VS Code

Connect to your local MySQL server.
NOTE: in VS Code I did this by creating a database profile using MySQL and linking the project folder

2. Run the Schema Script

Run the file:

    SQL/Schema.sql


This creates the database, tables, constraints, and the ReservationDetails view.

3. Run the Seed Script

Run the file:

    SQL/Seed.sql

This inserts sample room types, room statuses, rooms, guests, employees, and reservations.

4. Verify the Database

After running both SQL files, you can test the database with:

    USE hotel_reservation_db;
    SHOW TABLES;
    SELECT * FROM ReservationDetails;

Running the Application

Start the Flask application with in your terminal:

    python app.py

Then open the following address in your browser:

    http://127.0.0.1:5000

Main Routes

    /                       Dashboard
    /dashboard              Dashboard
    /guests                 View all guests
    /guests/new             Add guest
    /guests/<id>            View guest details
    /guests/<id>/edit       Edit guest
    /rooms                  View all rooms
    /rooms/new              Add room
    /rooms/<id>             View room details
    /rooms/<id>/edit        Edit room
    /room-types             View all room types
    /room-types/new         Add room type
    /room-types/<id>/edit   Edit room type
    /reservations           View all reservations
    /reservations/new       Add reservation
    /reservations/<id>      View reservation details
    /reservations/<id>/edit Edit reservation
    /db-test                Test database connection

Notes:
This application is intended for local development and school project use. The database connection is configured for a local MySQL server running on the developer's laptop.
The .env file is used to keep local database credentials separate from the source code.