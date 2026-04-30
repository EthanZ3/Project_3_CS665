-- Hotel Reservation Management System
-- Final 3NF Schema

CREATE DATABASE IF NOT EXISTS hotel_reservation_db;
USE hotel_reservation_db;

DROP VIEW IF EXISTS ReservationDetails;

DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS RoomStatuses;
DROP TABLE IF EXISTS RoomTypes;
DROP TABLE IF EXISTS Guests;
DROP TABLE IF EXISTS Employees;

-- RoomTypes
CREATE TABLE RoomTypes (
    roomTypeID INT PRIMARY KEY AUTO_INCREMENT,
    typeName VARCHAR(50) NOT NULL UNIQUE,
    maxOccupancy INT NOT NULL,
    basePrice DECIMAL(10, 2) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_roomtypes_max_occupancy
        CHECK (maxOccupancy > 0),

    CONSTRAINT chk_roomtypes_base_price
        CHECK (basePrice >= 0)
);

-- RoomStatuses
CREATE TABLE RoomStatuses (
    roomStatusID INT PRIMARY KEY AUTO_INCREMENT,
    statusName VARCHAR(20) NOT NULL UNIQUE
);

-- Rooms
CREATE TABLE Rooms (
    roomID INT PRIMARY KEY AUTO_INCREMENT,
    roomNumber VARCHAR(10) NOT NULL UNIQUE,
    roomStatusID INT NOT NULL,
    roomTypeID INT NOT NULL,
    floorNumber INT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rooms_room_status
        FOREIGN KEY (roomStatusID)
        REFERENCES RoomStatuses(roomStatusID),

    CONSTRAINT fk_rooms_room_type
        FOREIGN KEY (roomTypeID)
        REFERENCES RoomTypes(roomTypeID),

    CONSTRAINT chk_rooms_floor_number
        CHECK (floorNumber IS NULL OR floorNumber >= 0)
);

-- Guests
CREATE TABLE Guests (
    guestID INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(75) NOT NULL,
    lastName VARCHAR(75) NOT NULL,
    phoneNumber VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees
CREATE TABLE Employees (
    employeeID INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(75) NOT NULL,
    lastName VARCHAR(75) NOT NULL,
    jobTitle VARCHAR(50) NOT NULL,
    hireDate DATE NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reservations
CREATE TABLE Reservations (
    reservationID INT PRIMARY KEY AUTO_INCREMENT,
    guestID INT NOT NULL,
    roomID INT NOT NULL,
    employeeID INT,
    checkInDate DATE NOT NULL,
    checkOutDate DATE NOT NULL,

    numberOfNights INT
        GENERATED ALWAYS AS (DATEDIFF(checkOutDate, checkInDate)) STORED,

    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reservations_guest
        FOREIGN KEY (guestID)
        REFERENCES Guests(guestID),

    CONSTRAINT fk_reservations_room
        FOREIGN KEY (roomID)
        REFERENCES Rooms(roomID),

    CONSTRAINT fk_reservations_employee
        FOREIGN KEY (employeeID)
        REFERENCES Employees(employeeID),

    CONSTRAINT chk_reservations_dates
        CHECK (checkOutDate > checkInDate)
);

-- ReservationDetails View
-- Calculates finalCost without using triggers.
CREATE VIEW ReservationDetails AS
SELECT
    res.reservationID,
    res.guestID,
    CONCAT(g.firstName, ' ', g.lastName) AS guestName,
    res.roomID,
    rm.roomNumber,
    rt.roomTypeID,
    rt.typeName AS roomType,
    rt.basePrice,
    res.employeeID,
    CONCAT(e.firstName, ' ', e.lastName) AS employeeName,
    res.checkInDate,
    res.checkOutDate,
    res.numberOfNights,
    rt.basePrice * res.numberOfNights AS finalCost,
    res.createdAt
FROM Reservations res
JOIN Guests g
    ON res.guestID = g.guestID
JOIN Rooms rm
    ON res.roomID = rm.roomID
JOIN RoomTypes rt
    ON rm.roomTypeID = rt.roomTypeID
LEFT JOIN Employees e
    ON res.employeeID = e.employeeID;


SELECT * FROM ReservationDetails;