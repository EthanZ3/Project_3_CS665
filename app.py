from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import Config
from models import (
    db,
    Guest,
    Room,
    RoomType,
    RoomStatus,
    Employee,
    Reservation,
    ReservationDetails,
)


app = Flask(__name__)
app.config.from_object(Config)

# Connect Flask app to SQLAlchemy.
db.init_app(app)


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def get_or_404(model, object_id):
    """Get a database row by primary key or return a 404 page."""
    obj = db.session.get(model, object_id)

    if obj is None:
        abort(404)

    return obj


def clean_text(value):
    """Trim text fields and convert empty strings to None."""
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    return value


def parse_int(value, field_name, errors, required=True):
    """Safely parse integer form values."""
    value = clean_text(value)

    if value is None:
        if required:
            errors.append(f"{field_name} is required.")
        return None

    try:
        return int(value)
    except ValueError:
        errors.append(f"{field_name} must be a valid number.")
        return None


def parse_decimal(value, field_name, errors, required=True):
    """Safely parse decimal/money form values."""
    value = clean_text(value)

    if value is None:
        if required:
            errors.append(f"{field_name} is required.")
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        errors.append(f"{field_name} must be a valid decimal number.")
        return None


def parse_date(value, field_name, errors):
    """Safely parse date inputs from HTML date fields."""
    value = clean_text(value)

    if value is None:
        errors.append(f"{field_name} is required.")
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        errors.append(f"{field_name} must be a valid date.")
        return None


def get_status_by_name(status_name):
    """Find a room status by name."""
    return (
        RoomStatus.query
        .filter(func.lower(RoomStatus.statusName) == status_name.lower())
        .first()
    )


def mark_room_available_if_unused(room_id, excluding_reservation_id=None):
    """
    Set a room to Available if it has no other reservations.

    This is used after editing or deleting reservations.
    """
    available_status = get_status_by_name("Available")

    if available_status is None:
        return

    query = Reservation.query.filter(Reservation.roomID == room_id)

    if excluding_reservation_id is not None:
        query = query.filter(Reservation.reservationID != excluding_reservation_id)

    has_other_reservations = query.first() is not None

    if not has_other_reservations:
        room = db.session.get(Room, room_id)

        if room:
            room.roomStatusID = available_status.roomStatusID


def get_room_rows():
    """Get rooms with their type, status, and base price for list/dropdown pages."""
    return (
        db.session.query(
            Room.roomID,
            Room.roomNumber,
            Room.roomStatusID,
            Room.roomTypeID,
            Room.floorNumber,
            Room.createdAt,
            RoomType.typeName,
            RoomType.basePrice,
            RoomStatus.statusName,
        )
        .join(RoomType, Room.roomTypeID == RoomType.roomTypeID)
        .join(RoomStatus, Room.roomStatusID == RoomStatus.roomStatusID)
        .order_by(Room.roomNumber)
        .all()
    )


# ------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------

def validate_guest_form(guest_id=None):
    """Server-side validation for guest create/update."""
    errors = []

    first_name = clean_text(request.form.get("firstName"))
    last_name = clean_text(request.form.get("lastName"))
    phone_number = clean_text(request.form.get("phoneNumber"))
    email = clean_text(request.form.get("email"))

    if not first_name:
        errors.append("First name is required.")

    if not last_name:
        errors.append("Last name is required.")

    if email:
        query = Guest.query.filter(func.lower(Guest.email) == email.lower())

        if guest_id is not None:
            query = query.filter(Guest.guestID != guest_id)

        if query.first():
            errors.append("That email is already being used by another guest.")

    data = {
        "firstName": first_name,
        "lastName": last_name,
        "phoneNumber": phone_number,
        "email": email,
    }

    return data, errors


def validate_room_type_form(room_type_id=None):
    """Server-side validation for room type create/update."""
    errors = []

    type_name = clean_text(request.form.get("typeName"))
    max_occupancy = parse_int(request.form.get("maxOccupancy"), "Max occupancy", errors)
    base_price = parse_decimal(request.form.get("basePrice"), "Base price", errors)

    if not type_name:
        errors.append("Room type name is required.")

    if max_occupancy is not None and max_occupancy <= 0:
        errors.append("Max occupancy must be greater than 0.")

    if base_price is not None and base_price < 0:
        errors.append("Base price cannot be negative.")

    if type_name:
        query = RoomType.query.filter(func.lower(RoomType.typeName) == type_name.lower())

        if room_type_id is not None:
            query = query.filter(RoomType.roomTypeID != room_type_id)

        if query.first():
            errors.append("That room type already exists.")

    data = {
        "typeName": type_name,
        "maxOccupancy": max_occupancy,
        "basePrice": base_price,
    }

    return data, errors


def validate_room_form(room_id=None):
    """Server-side validation for room create/update."""
    errors = []

    room_number = clean_text(request.form.get("roomNumber"))
    room_type_id = parse_int(request.form.get("roomTypeID"), "Room type", errors)
    room_status_id = parse_int(request.form.get("roomStatusID"), "Room status", errors)
    floor_number = parse_int(request.form.get("floorNumber"), "Floor number", errors, required=False)

    if not room_number:
        errors.append("Room number is required.")

    if floor_number is not None and floor_number < 0:
        errors.append("Floor number cannot be negative.")

    if room_type_id is not None and db.session.get(RoomType, room_type_id) is None:
        errors.append("Selected room type does not exist.")

    if room_status_id is not None and db.session.get(RoomStatus, room_status_id) is None:
        errors.append("Selected room status does not exist.")

    if room_number:
        query = Room.query.filter(func.lower(Room.roomNumber) == room_number.lower())

        if room_id is not None:
            query = query.filter(Room.roomID != room_id)

        if query.first():
            errors.append("That room number already exists.")

    data = {
        "roomNumber": room_number,
        "roomTypeID": room_type_id,
        "roomStatusID": room_status_id,
        "floorNumber": floor_number,
    }

    return data, errors


def validate_reservation_form(reservation_id=None):
    """Server-side validation for reservation create/update."""
    errors = []

    guest_id = parse_int(request.form.get("guestID"), "Guest", errors)
    room_id = parse_int(request.form.get("roomID"), "Room", errors)
    employee_id = parse_int(request.form.get("employeeID"), "Employee", errors, required=False)
    check_in_date = parse_date(request.form.get("checkInDate"), "Check-in date", errors)
    check_out_date = parse_date(request.form.get("checkOutDate"), "Check-out date", errors)

    guest = None
    room = None
    employee = None

    if guest_id is not None:
        guest = db.session.get(Guest, guest_id)

        if guest is None:
            errors.append("Selected guest does not exist.")

    if room_id is not None:
        room = db.session.get(Room, room_id)

        if room is None:
            errors.append("Selected room does not exist.")

    if employee_id is not None:
        employee = db.session.get(Employee, employee_id)

        if employee is None:
            errors.append("Selected employee does not exist.")

    if check_in_date and check_out_date:
        if check_out_date <= check_in_date:
            errors.append("Check-out date must be after check-in date.")

    # Prevent overlapping reservations for the same room.
    if room_id and check_in_date and check_out_date and check_out_date > check_in_date:
        overlap_query = Reservation.query.filter(
            Reservation.roomID == room_id,
            Reservation.checkInDate < check_out_date,
            Reservation.checkOutDate > check_in_date,
        )

        if reservation_id is not None:
            overlap_query = overlap_query.filter(Reservation.reservationID != reservation_id)

        if overlap_query.first():
            errors.append("This room already has a reservation that overlaps those dates.")

    data = {
        "guestID": guest_id,
        "roomID": room_id,
        "employeeID": employee_id,
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date,
        "guest": guest,
        "room": room,
        "employee": employee,
    }

    return data, errors


def flash_errors(errors):
    """Display validation errors using Flask flash messages."""
    for error in errors:
        flash(error, "danger")


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

@app.route("/")
@app.route("/dashboard")
def dashboard():
    """Dashboard using SQL aggregate functions."""
    total_guests = db.session.query(func.count(Guest.guestID)).scalar() or 0
    total_rooms = db.session.query(func.count(Room.roomID)).scalar() or 0
    total_reservations = db.session.query(func.count(Reservation.reservationID)).scalar() or 0

    total_revenue = (
        db.session.query(func.coalesce(func.sum(ReservationDetails.finalCost), 0))
        .scalar()
        or 0
    )

    avg_reservation_value = (
        db.session.query(func.coalesce(func.avg(ReservationDetails.finalCost), 0))
        .scalar()
        or 0
    )

    avg_stay_length = (
        db.session.query(func.coalesce(func.avg(Reservation.numberOfNights), 0))
        .scalar()
        or 0
    )

    available_rooms = (
        db.session.query(func.count(Room.roomID))
        .join(RoomStatus, Room.roomStatusID == RoomStatus.roomStatusID)
        .filter(func.lower(RoomStatus.statusName) == "available")
        .scalar()
        or 0
    )

    busy_rooms = (
        db.session.query(func.count(Room.roomID))
        .join(RoomStatus, Room.roomStatusID == RoomStatus.roomStatusID)
        .filter(func.lower(RoomStatus.statusName).in_(["occupied", "reserved"]))
        .scalar()
        or 0
    )

    stats = {
        "total_guests": total_guests,
        "total_rooms": total_rooms,
        "total_reservations": total_reservations,
        "total_revenue": total_revenue,
        "avg_reservation_value": avg_reservation_value,
        "avg_stay_length": avg_stay_length,
        "available_rooms": available_rooms,
        "busy_rooms": busy_rooms,
    }

    room_status_summary = (
        db.session.query(
            RoomStatus.statusName,
            func.count(Room.roomID).label("roomCount"),
        )
        .outerjoin(Room, RoomStatus.roomStatusID == Room.roomStatusID)
        .group_by(RoomStatus.roomStatusID, RoomStatus.statusName)
        .order_by(RoomStatus.statusName)
        .all()
    )

    room_type_summary = (
        db.session.query(
            ReservationDetails.roomType,
            func.count(ReservationDetails.reservationID).label("reservationCount"),
            func.coalesce(func.sum(ReservationDetails.finalCost), 0).label("revenue"),
        )
        .group_by(ReservationDetails.roomType)
        .order_by(ReservationDetails.roomType)
        .all()
    )

    recent_reservations = (
        ReservationDetails.query
        .order_by(ReservationDetails.createdAt.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        title="Dashboard",
        stats=stats,
        room_status_summary=room_status_summary,
        room_type_summary=room_type_summary,
        recent_reservations=recent_reservations,
    )


@app.route("/db-test")
def db_test():
    """Simple test route to confirm the database connection works."""
    total_guests = db.session.query(func.count(Guest.guestID)).scalar()
    return f"Database connected. Total guests: {total_guests}"


# ------------------------------------------------------------
# Guests CRUD
# ------------------------------------------------------------

@app.route("/guests")
def list_guests():
    guests = Guest.query.order_by(Guest.lastName, Guest.firstName).all()

    return render_template(
        "guests/list.html",
        title="Guests",
        guests=guests,
    )


@app.route("/guests/<int:guest_id>")
def show_guest(guest_id):
    guest = get_or_404(Guest, guest_id)

    reservations = (
        ReservationDetails.query
        .filter(ReservationDetails.guestID == guest_id)
        .order_by(ReservationDetails.checkInDate.desc())
        .all()
    )

    return render_template(
        "guests/detail.html",
        title="Guest Details",
        guest=guest,
        reservations=reservations,
    )


@app.route("/guests/new", methods=["GET", "POST"])
def create_guest():
    if request.method == "POST":
        data, errors = validate_guest_form()

        if errors:
            flash_errors(errors)
            return render_template("guests/form.html", title="Add Guest", guest=data)

        guest = Guest(**data)

        try:
            db.session.add(guest)
            db.session.commit()
            flash("Guest created successfully.", "success")
            return redirect(url_for("list_guests"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not create guest because of a duplicate or invalid value.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while creating the guest.", "danger")

    return render_template("guests/form.html", title="Add Guest", guest=None)


@app.route("/guests/<int:guest_id>/edit", methods=["GET", "POST"])
def edit_guest(guest_id):
    guest = get_or_404(Guest, guest_id)

    if request.method == "POST":
        data, errors = validate_guest_form(guest_id)

        if errors:
            flash_errors(errors)
            return render_template("guests/form.html", title="Edit Guest", guest=guest)

        guest.firstName = data["firstName"]
        guest.lastName = data["lastName"]
        guest.phoneNumber = data["phoneNumber"]
        guest.email = data["email"]

        try:
            db.session.commit()
            flash("Guest updated successfully.", "success")
            return redirect(url_for("show_guest", guest_id=guest.guestID))
        except IntegrityError:
            db.session.rollback()
            flash("Could not update guest because of a duplicate or invalid value.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while updating the guest.", "danger")

    return render_template("guests/form.html", title="Edit Guest", guest=guest)


@app.route("/guests/<int:guest_id>/delete", methods=["POST"])
def delete_guest(guest_id):
    guest = get_or_404(Guest, guest_id)

    if Reservation.query.filter_by(guestID=guest_id).first():
        flash("Cannot delete this guest because they have reservations.", "warning")
        return redirect(url_for("list_guests"))

    try:
        db.session.delete(guest)
        db.session.commit()
        flash("Guest deleted successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("A database error occurred while deleting the guest.", "danger")

    return redirect(url_for("list_guests"))


# ------------------------------------------------------------
# RoomTypes CRUD
# ------------------------------------------------------------

@app.route("/room-types")
def list_room_types():
    room_types = RoomType.query.order_by(RoomType.typeName).all()

    return render_template(
        "room_types/list.html",
        title="Room Types",
        room_types=room_types,
    )


@app.route("/room-types/new", methods=["GET", "POST"])
def create_room_type():
    if request.method == "POST":
        data, errors = validate_room_type_form()

        if errors:
            flash_errors(errors)
            return render_template("room_types/form.html", title="Add Room Type", room_type=data)

        room_type = RoomType(**data)

        try:
            db.session.add(room_type)
            db.session.commit()
            flash("Room type created successfully.", "success")
            return redirect(url_for("list_room_types"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not create room type because of a duplicate or invalid value.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while creating the room type.", "danger")

    return render_template("room_types/form.html", title="Add Room Type", room_type=None)


@app.route("/room-types/<int:room_type_id>/edit", methods=["GET", "POST"])
def edit_room_type(room_type_id):
    room_type = get_or_404(RoomType, room_type_id)

    if request.method == "POST":
        data, errors = validate_room_type_form(room_type_id)

        if errors:
            flash_errors(errors)
            return render_template("room_types/form.html", title="Edit Room Type", room_type=room_type)

        room_type.typeName = data["typeName"]
        room_type.maxOccupancy = data["maxOccupancy"]
        room_type.basePrice = data["basePrice"]

        try:
            db.session.commit()
            flash("Room type updated successfully.", "success")
            return redirect(url_for("list_room_types"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not update room type because of a duplicate or invalid value.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while updating the room type.", "danger")

    return render_template("room_types/form.html", title="Edit Room Type", room_type=room_type)


@app.route("/room-types/<int:room_type_id>/delete", methods=["POST"])
def delete_room_type(room_type_id):
    room_type = get_or_404(RoomType, room_type_id)

    if Room.query.filter_by(roomTypeID=room_type_id).first():
        flash("Cannot delete this room type because rooms are using it.", "warning")
        return redirect(url_for("list_room_types"))

    try:
        db.session.delete(room_type)
        db.session.commit()
        flash("Room type deleted successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("A database error occurred while deleting the room type.", "danger")

    return redirect(url_for("list_room_types"))


# ------------------------------------------------------------
# Rooms CRUD
# ------------------------------------------------------------

@app.route("/rooms")
def list_rooms():
    rooms = get_room_rows()

    return render_template(
        "rooms/list.html",
        title="Rooms",
        rooms=rooms,
    )


@app.route("/rooms/<int:room_id>")
def show_room(room_id):
    room = (
        db.session.query(
            Room.roomID,
            Room.roomNumber,
            Room.floorNumber,
            Room.createdAt,
            RoomType.typeName,
            RoomType.basePrice,
            RoomStatus.statusName,
        )
        .join(RoomType, Room.roomTypeID == RoomType.roomTypeID)
        .join(RoomStatus, Room.roomStatusID == RoomStatus.roomStatusID)
        .filter(Room.roomID == room_id)
        .first()
    )

    if room is None:
        abort(404)

    reservations = (
        ReservationDetails.query
        .filter(ReservationDetails.roomID == room_id)
        .order_by(ReservationDetails.checkInDate.desc())
        .all()
    )

    return render_template(
        "rooms/detail.html",
        title="Room Details",
        room=room,
        reservations=reservations,
    )


@app.route("/rooms/new", methods=["GET", "POST"])
def create_room():
    room_types = RoomType.query.order_by(RoomType.typeName).all()
    room_statuses = RoomStatus.query.order_by(RoomStatus.statusName).all()

    if request.method == "POST":
        data, errors = validate_room_form()

        if errors:
            flash_errors(errors)
            return render_template(
                "rooms/form.html",
                title="Add Room",
                room=data,
                room_types=room_types,
                room_statuses=room_statuses,
            )

        room = Room(**data)

        try:
            db.session.add(room)
            db.session.commit()
            flash("Room created successfully.", "success")
            return redirect(url_for("list_rooms"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not create room because of a duplicate or invalid value.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while creating the room.", "danger")

    return render_template(
        "rooms/form.html",
        title="Add Room",
        room=None,
        room_types=room_types,
        room_statuses=room_statuses,
    )


@app.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
def edit_room(room_id):
    room = get_or_404(Room, room_id)
    room_types = RoomType.query.order_by(RoomType.typeName).all()
    room_statuses = RoomStatus.query.order_by(RoomStatus.statusName).all()

    if request.method == "POST":
        data, errors = validate_room_form(room_id)

        if errors:
            flash_errors(errors)
            return render_template(
                "rooms/form.html",
                title="Edit Room",
                room=room,
                room_types=room_types,
                room_statuses=room_statuses,
            )

        room.roomNumber = data["roomNumber"]
        room.roomTypeID = data["roomTypeID"]
        room.roomStatusID = data["roomStatusID"]
        room.floorNumber = data["floorNumber"]

        try:
            db.session.commit()
            flash("Room updated successfully.", "success")
            return redirect(url_for("show_room", room_id=room.roomID))
        except IntegrityError:
            db.session.rollback()
            flash("Could not update room because of a duplicate or invalid value.", "danger")
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while updating the room.", "danger")

    return render_template(
        "rooms/form.html",
        title="Edit Room",
        room=room,
        room_types=room_types,
        room_statuses=room_statuses,
    )


@app.route("/rooms/<int:room_id>/delete", methods=["POST"])
def delete_room(room_id):
    room = get_or_404(Room, room_id)

    if Reservation.query.filter_by(roomID=room_id).first():
        flash("Cannot delete this room because it has reservations.", "warning")
        return redirect(url_for("list_rooms"))

    try:
        db.session.delete(room)
        db.session.commit()
        flash("Room deleted successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("A database error occurred while deleting the room.", "danger")

    return redirect(url_for("list_rooms"))


# ------------------------------------------------------------
# Reservations CRUD
# ------------------------------------------------------------

@app.route("/reservations")
def list_reservations():
    reservations = (
        ReservationDetails.query
        .order_by(ReservationDetails.checkInDate.desc())
        .all()
    )

    return render_template(
        "reservations/list.html",
        title="Reservations",
        reservations=reservations,
    )


@app.route("/reservations/<int:reservation_id>")
def show_reservation(reservation_id):
    reservation = (
        ReservationDetails.query
        .filter(ReservationDetails.reservationID == reservation_id)
        .first()
    )

    if reservation is None:
        abort(404)

    return render_template(
        "reservations/detail.html",
        title="Reservation Details",
        reservation=reservation,
    )


@app.route("/reservations/new", methods=["GET", "POST"])
def create_reservation():
    guests = Guest.query.order_by(Guest.lastName, Guest.firstName).all()
    rooms = get_room_rows()
    employees = Employee.query.order_by(Employee.lastName, Employee.firstName).all()

    if request.method == "POST":
        data, errors = validate_reservation_form()

        reserved_status = get_status_by_name("Reserved")

        if reserved_status is None:
            errors.append("Room status 'Reserved' does not exist in the database.")

        if errors:
            flash_errors(errors)
            return render_template(
                "reservations/form.html",
                title="Add Reservation",
                reservation=data,
                guests=guests,
                rooms=rooms,
                employees=employees,
            )

        reservation = Reservation(
            guestID=data["guestID"],
            roomID=data["roomID"],
            employeeID=data["employeeID"],
            checkInDate=data["checkInDate"],
            checkOutDate=data["checkOutDate"],
        )

        # Transaction logic:
        # Step 1: insert reservation.
        # Step 2: update room status to Reserved.
        # Step 3: commit both together.
        # If anything fails, rollback both.
        try:
            db.session.add(reservation)
            data["room"].roomStatusID = reserved_status.roomStatusID
            db.session.commit()

            flash("Reservation created and room status updated successfully.", "success")
            return redirect(url_for("list_reservations"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while creating the reservation.", "danger")

    return render_template(
        "reservations/form.html",
        title="Add Reservation",
        reservation=None,
        guests=guests,
        rooms=rooms,
        employees=employees,
    )


@app.route("/reservations/<int:reservation_id>/edit", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    reservation = get_or_404(Reservation, reservation_id)

    guests = Guest.query.order_by(Guest.lastName, Guest.firstName).all()
    rooms = get_room_rows()
    employees = Employee.query.order_by(Employee.lastName, Employee.firstName).all()

    if request.method == "POST":
        old_room_id = reservation.roomID
        data, errors = validate_reservation_form(reservation_id)

        reserved_status = get_status_by_name("Reserved")

        if reserved_status is None:
            errors.append("Room status 'Reserved' does not exist in the database.")

        if errors:
            flash_errors(errors)
            return render_template(
                "reservations/form.html",
                title="Edit Reservation",
                reservation=reservation,
                guests=guests,
                rooms=rooms,
                employees=employees,
            )

        try:
            reservation.guestID = data["guestID"]
            reservation.roomID = data["roomID"]
            reservation.employeeID = data["employeeID"]
            reservation.checkInDate = data["checkInDate"]
            reservation.checkOutDate = data["checkOutDate"]

            data["room"].roomStatusID = reserved_status.roomStatusID

            if old_room_id != data["roomID"]:
                mark_room_available_if_unused(old_room_id, excluding_reservation_id=reservation_id)

            db.session.commit()
            flash("Reservation updated successfully.", "success")
            return redirect(url_for("show_reservation", reservation_id=reservation.reservationID))
        except SQLAlchemyError:
            db.session.rollback()
            flash("A database error occurred while updating the reservation.", "danger")

    return render_template(
        "reservations/form.html",
        title="Edit Reservation",
        reservation=reservation,
        guests=guests,
        rooms=rooms,
        employees=employees,
    )


@app.route("/reservations/<int:reservation_id>/delete", methods=["POST"])
def delete_reservation(reservation_id):
    reservation = get_or_404(Reservation, reservation_id)
    room_id = reservation.roomID

    try:
        db.session.delete(reservation)
        mark_room_available_if_unused(room_id, excluding_reservation_id=reservation_id)
        db.session.commit()

        flash("Reservation deleted successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("A database error occurred while deleting the reservation.", "danger")

    return redirect(url_for("list_reservations"))


if __name__ == "__main__":
    app.run(debug=True)