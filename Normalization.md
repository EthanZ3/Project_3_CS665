Original schema:
RoomTypes
- roomTypeID PK
- typeName
- maxOccupancy
- basePrice
- createdAt

Rooms
- roomID PK
- roomNumber UNIQUE
- roomTypeID FK
- roomStatus
- floorNumber
- createdAt

Guests
- guestID PK
- firstName
- lastName
- phoneNumber
- email
- createdAt

Employees
- employeeID PK
- firstName
- lastName
- jobTitle
- hireDate
- createdAt

Reservations
- reservationID PK
- guestID FK
- roomID FK
- employeeID FK
- checkInDate
- checkOutDate
- totalAmount
- createdAt


Original Functional Dependencies:
RoomTypes:
- roomTypeID -> typeName, maxOccupancy, basePrice, createdAt
- typeName -> roomTypeID, maxOccupancy, basePrice, createdAt

Rooms:
- roomID -> roomNumber, roomTypeID, roomStatus, floorNumber, createdAt
- roomNumber -> roomID, roomTypeID, roomStatus, floorNumber, createdAt

Guests:
- guestID -> firstName, lastName, phoneNumber, email, createdAt
- email -> guestID, firstName, lastName, phoneNumber, createdAt

Employees:
- employeeID -> firstName, lastName, jobTitle, hireDate, createdAt

Reservations:
- reservationID -> guestID, roomID, employeeID, checkInDate, checkOutDate, totalAmount, createdAt


Anomalies:
Anomaly Identification

First, the `Rooms` table stored `roomStatus` as a plain text value. This could cause update anomalies and inconsistent data. For example, one room could be marked as `Available`, another as `available`, and another as `Availible`. These values would mean the same thing to a user, but the database would treat them as different values.

- roomStatus was plain text which could lead to issues wher available and Available could exist at the same time this could cause an update anomaly
- numberOfNights was originally added later but is now part of the main database because checkInDate and checkOutDate are both required
- totalAmount was renamed to finalCost for clarity and like numberOfNights updates automatically and is calculated from basePrice times numberOfNights


Decomposition:
Summary steps:
1. Create RoomStatuses table so that we can reference a value that stores a status rather than plain text
2. Replace roomStatus with roomStatusID to update the table to match our new changes so that it works properly
3. Update Reservations calculated fields. The numberOfNights field is generated from checkInDate and checkOutDate. The finalCost is calculated in the ReservationDetails view using`RoomTypes.basePrice * numberOfNights.
- RoomTypes -> roomTypeID PK, typeName, maxOccupancy, basePrice, createdAt

- RoomStatuses -> roomStatusID PK, statusName

- Rooms -> roomID PK, roomNumber UNIQUE, roomStatusID FK, roomTypeID FK, floorNumber, createdAt

- Guests -> guestID PK, firstName, lastName, phoneNumber, email, createdAt

- Employees -> employeeID PK, firstName, lastName, jobTitle, hireDate, createdAt

- Reservations -> reservationID PK, guestID FK, roomID FK, employeeID FK, checkInDate, checkOutDate, numberOfNights, createdAt

- ReservationDetails View -> reservationID, guestID, guestName, roomID, roomNumber, roomTypeID, roomType, basePrice, employeeID, employeeName, checkInDate, checkOutDate, numberOfNights, finalCost, createdAt
- changed the name of totalAmount to finalCost to be more clear.

Final Schema:

RoomTypes
- roomTypeID INT PRIMARY KEY AUTO_INCREMENT
- typeName VARCHAR(50) NOT NULL UNIQUE
- maxOccupancy INT NOT NULL
- basePrice DECIMAL(10, 2) NOT NULL
- createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP

RoomStatuses
- roomStatusID INT PRIMARY KEY AUTO_INCREMENT
- statusName VARCHAR(20) NOT NULL UNIQUE

Rooms
- roomID INT PRIMARY KEY AUTO_INCREMENT
- roomNumber VARCHAR(10) NOT NULL UNIQUE
- roomStatusID INT NOT NULL FOREIGN KEY REFERENCES RoomStatuses(roomStatusID)
- roomTypeID INT NOT NULL FOREIGN KEY REFERENCES RoomTypes(roomTypeID)
- floorNumber INT
- createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Guests
- guestID INT PRIMARY KEY AUTO_INCREMENT
- firstName VARCHAR(75) NOT NULL
- lastName VARCHAR(75) NOT NULL
- phoneNumber VARCHAR(15)
- email VARCHAR(100) UNIQUE
- createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Employees
- employeeID INT PRIMARY KEY AUTO_INCREMENT
- firstName VARCHAR(75) NOT NULL
- lastName VARCHAR(75) NOT NULL
- jobTitle VARCHAR(50) NOT NULL
- hireDate DATE NOT NULL
- createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Reservations
- reservationID INT PRIMARY KEY AUTO_INCREMENT
- guestID INT NOT NULL FOREIGN KEY REFERENCES Guests(guestID)
- roomID INT NOT NULL FOREIGN KEY REFERENCES Rooms(roomID)
- employeeID INT FOREIGN KEY REFERENCES Employees(employeeID)
- checkInDate DATE NOT NULL
- checkOutDate DATE NOT NULL
- numberOfNights INT GENERATED FROM checkInDate and checkOutDate
- createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP

ReservationDetails View
- reservationID
- guestID
- guestName
- roomID
- roomNumber
- roomTypeID
- roomType
- basePrice
- employeeID
- employeeName
- checkInDate
- checkOutDate
- numberOfNights
- finalCost CALCULATED FROM RoomTypes.basePrice × numberOfNights
- createdAt