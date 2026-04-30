from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Computed

db = SQLAlchemy()


class RoomType(db.Model):
    __tablename__ = "RoomTypes"

    roomTypeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    typeName = db.Column(db.String(50), nullable=False, unique=True)
    maxOccupancy = db.Column(db.Integer, nullable=False)
    basePrice = db.Column(db.Numeric(10, 2), nullable=False)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    rooms = db.relationship("Room", back_populates="room_type")

    __table_args__ = (
        CheckConstraint("maxOccupancy > 0", name="chk_roomtypes_max_occupancy"),
        CheckConstraint("basePrice >= 0", name="chk_roomtypes_base_price"),
    )


class RoomStatus(db.Model):
    __tablename__ = "RoomStatuses"

    roomStatusID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    statusName = db.Column(db.String(20), nullable=False, unique=True)

    rooms = db.relationship("Room", back_populates="status")


class Room(db.Model):
    __tablename__ = "Rooms"

    roomID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roomNumber = db.Column(db.String(10), nullable=False, unique=True)
    roomStatusID = db.Column(
        db.Integer,
        db.ForeignKey("RoomStatuses.roomStatusID"),
        nullable=False
    )
    roomTypeID = db.Column(
        db.Integer,
        db.ForeignKey("RoomTypes.roomTypeID"),
        nullable=False
    )
    floorNumber = db.Column(db.Integer)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    status = db.relationship("RoomStatus", back_populates="rooms")
    room_type = db.relationship("RoomType", back_populates="rooms")
    reservations = db.relationship("Reservation", back_populates="room")

    __table_args__ = (
        CheckConstraint(
            "floorNumber IS NULL OR floorNumber >= 0",
            name="chk_rooms_floor_number"
        ),
    )


class Guest(db.Model):
    __tablename__ = "Guests"

    guestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(75), nullable=False)
    lastName = db.Column(db.String(75), nullable=False)
    phoneNumber = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    reservations = db.relationship("Reservation", back_populates="guest")


class Employee(db.Model):
    __tablename__ = "Employees"

    employeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(75), nullable=False)
    lastName = db.Column(db.String(75), nullable=False)
    jobTitle = db.Column(db.String(50), nullable=False)
    hireDate = db.Column(db.Date, nullable=False)
    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    reservations = db.relationship("Reservation", back_populates="employee")


class Reservation(db.Model):
    __tablename__ = "Reservations"

    reservationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guestID = db.Column(
        db.Integer,
        db.ForeignKey("Guests.guestID"),
        nullable=False
    )
    roomID = db.Column(
        db.Integer,
        db.ForeignKey("Rooms.roomID"),
        nullable=False
    )
    employeeID = db.Column(
        db.Integer,
        db.ForeignKey("Employees.employeeID"),
        nullable=True
    )
    checkInDate = db.Column(db.Date, nullable=False)
    checkOutDate = db.Column(db.Date, nullable=False)

    numberOfNights = db.Column(
        db.Integer,
        Computed("DATEDIFF(checkOutDate, checkInDate)", persisted=True)
    )

    createdAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    guest = db.relationship("Guest", back_populates="reservations")
    room = db.relationship("Room", back_populates="reservations")
    employee = db.relationship("Employee", back_populates="reservations")

    __table_args__ = (
        CheckConstraint(
            "checkOutDate > checkInDate",
            name="chk_reservations_dates"
        ),
    )


class ReservationDetails(db.Model):
    """
    SQLAlchemy model for the ReservationDetails database view.

    This is read-only in practice. Use Reservation for inserts/updates/deletes.
    """
    __tablename__ = "ReservationDetails"

    reservationID = db.Column(db.Integer, primary_key=True)
    guestID = db.Column(db.Integer)
    guestName = db.Column(db.String(151))
    roomID = db.Column(db.Integer)
    roomNumber = db.Column(db.String(10))
    roomTypeID = db.Column(db.Integer)
    roomType = db.Column(db.String(50))
    basePrice = db.Column(db.Numeric(10, 2))
    employeeID = db.Column(db.Integer)
    employeeName = db.Column(db.String(151))
    checkInDate = db.Column(db.Date)
    checkOutDate = db.Column(db.Date)
    numberOfNights = db.Column(db.Integer)
    finalCost = db.Column(db.Numeric(10, 2))
    createdAt = db.Column(db.DateTime)