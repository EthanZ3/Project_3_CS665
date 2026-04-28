USE hotel_reservation_db;

INSERT INTO RoomTypes (typeName, maxOccupancy, basePrice) VALUES
('Single', 1, 75.00),
('Double', 2, 100.00),
('Queen', 2, 120.00),
('King', 2, 150.00),
('Suite', 4, 250.00);

INSERT INTO RoomStatuses (statusName) VALUES
('Occupied'),
('Available'),
('Cleaning'),
('Reserved');

INSERT INTO Rooms (roomNumber, roomTypeID, floorNumber, roomStatusID) VALUES
('101', 1, 1, 1),
('102', 2, 1, 2),
('201', 3, 2, 3),
('202', 4, 2, 3),
('301', 5, 3, 2);

INSERT INTO Guests (firstName, lastName, phoneNumber, email) VALUES
('John', 'Doe', '555-1111', 'john@email.com'),
('Tony', 'Stark', '555-2222', 'tony@email.com'),
('Barney', 'Dinosaur', '555-3333', 'barney@email.com'),
('Bruce', 'Wayne', '555-4444', 'bruce@email.com'),
('Sponge', 'Bob', '555-5555', 'sponge@email.com');

INSERT INTO Employees (firstName, lastName, jobTitle, hireDate) VALUES
('Managebot', '100', 'Manager', '2022-01-10'),
('Deskbot', 'T-800', 'Front Desk', '2023-03-15'),
('Maintainbot', 'Mark 1', 'Maintenance', '2023-06-01'),
('Cleaningbot', '001', 'Housekeeping', '2024-02-20'),
('Roomba', 'Shark', 'Housekeeping', '2024-01-01');

INSERT INTO Reservations 
(guestID, roomID, employeeID, checkInDate, checkOutDate) 
VALUES
(1, 1, 2, '2026-04-10', '2026-04-12'),
(2, 2, 2, '2026-03-11', '2026-03-13'),
(3, 3, 4, '2026-04-12', '2026-04-15'),
(4, 4, 5, '2026-03-13', '2026-03-14'),
(5, 5, 2, '2026-05-14', '2026-05-17');