-- ============================================================================
-- Comprehensive Seed Data for Transport Management System Demo
-- ============================================================================

-- VEHICLES
INSERT INTO vehicles (plate_number, make, model, year, capacity, status, mileage, fuel_type) VALUES
('KCA-001-A', 'Toyota', 'Hiace', 2022, 14, 'Available', 15000, 'Diesel'),
('KCA-002-B', 'Mercedes', 'Sprinter', 2023, 16, 'Available', 8000, 'Diesel'),
('KCA-003-C', 'Nissan', 'Urvan', 2021, 12, 'In Maintenance', 25000, 'Petrol'),
('KCA-004-D', 'Toyota', 'Coaster', 2020, 30, 'Available', 45000, 'Diesel'),
('KCA-005-E', 'Hyundai', 'H350', 2022, 20, 'Available', 12000, 'Diesel');
GO

-- ROUTES
INSERT INTO routes (origin, destination, distance_km, duration_minutes, status) VALUES
('Nairobi CBD', 'Karen', 15.5, 35, 'Active'),
('Nairobi CBD', 'Ngong', 25.0, 50, 'Active'),
('Nairobi CBD', 'Westlands', 8.0, 20, 'Active'),
('Nairobi CBD', 'South C', 12.0, 30, 'Active'),
('Nairobi CBD', 'Kilimani', 10.0, 25, 'Active'),
('Kilimani', 'Langata', 20.0, 45, 'Active'),
('Westlands', 'Runda', 5.0, 15, 'Active');
GO

-- DRIVERS
INSERT INTO drivers (user_id, name, license_number, phone, status, assigned_vehicle_id) VALUES
(NULL, 'Joseph Kipchoge', 'DL-2023-001', '+254712345678', 'Available', 1),
(NULL, 'Samuel Mwangi', 'DL-2023-002', '+254713456789', 'On Duty', 2),
(NULL, 'David Kariuki', 'DL-2023-003', '+254714567890', 'On Break', NULL),
(NULL, 'Peter Ochieng', 'DL-2023-004', '+254715678901', 'Available', 4),
(NULL, 'James Kiplagat', 'DL-2023-005', '+254716789012', 'Available', 5);
GO

-- ASSIGNMENTS (Driver to Vehicle to Route)
INSERT INTO assignments (vehicle_id, driver_id, route_id, start_date, end_date, status, monthly_fare) VALUES
(1, 1, 1, '2026-05-01', NULL, 'Active', 750.00),
(2, 2, 2, '2026-05-01', NULL, 'Active', 850.00),
(4, 4, 4, '2026-05-01', NULL, 'Active', 950.00),
(5, 5, 5, '2026-05-01', NULL, 'Active', 800.00);
GO

-- SCHEDULES (Trips)
INSERT INTO schedules (assignment_id, departure_time, arrival_time, status) VALUES
(1, '2026-05-30 06:30:00', '2026-05-30 07:15:00', 'Completed'),
(1, '2026-05-30 08:00:00', '2026-05-30 08:45:00', 'Completed'),
(1, '2026-05-30 15:00:00', '2026-05-30 15:45:00', 'In Progress'),
(2, '2026-05-30 07:00:00', '2026-05-30 08:15:00', 'Completed'),
(2, '2026-05-30 16:00:00', '2026-05-30 17:15:00', 'Scheduled'),
(3, '2026-05-30 06:00:00', '2026-05-30 06:50:00', 'Completed'),
(4, '2026-05-30 07:30:00', '2026-05-30 08:10:00', 'Completed');
GO

-- PASSENGERS (user_ids 6-12 correspond to passenger02-passenger08; passenger01 is seeded by Python)
INSERT INTO passengers (user_id, name, phone, outstanding_balance) VALUES
(6, 'Mary Njeri', '+254720111111', 500.00),
(7, 'John Kamau', '+254720222222', 0.00),
(8, 'Alice Wanjiru', '+254720333333', 1200.00),
(9, 'Robert Muiyuro', '+254720444444', 250.00),
(10, 'Grace Kamande', '+254720555555', 0.00),
(11, 'Daniel Omondi', '+254720666666', 800.00),
(12, 'Susan Kipchoge', '+254720777777', 350.00);
GO

-- BOOKINGS
INSERT INTO bookings (passenger_id, assignment_id, booking_date, status) VALUES
(1, 1, '2026-05-30 06:15:00', 'Completed'),
(2, 1, '2026-05-30 06:20:00', 'Completed'),
(3, 1, '2026-05-30 06:25:00', 'Completed'),
(1, 2, '2026-05-30 15:30:00', 'Confirmed'),
(4, 2, '2026-05-30 16:45:00', 'Confirmed'),
(5, 3, '2026-05-30 06:00:00', 'Completed'),
(6, 3, '2026-05-30 06:05:00', 'Completed'),
(7, 4, '2026-05-30 07:15:00', 'Completed'),
(8, 4, '2026-05-30 07:20:00', 'Completed');
GO

-- TRANSPORT FEES
INSERT INTO transport_fees (passenger_id, assignment_id, amount, month_year, due_date, status) VALUES
(1, 1, 500.00, 'May 2026', '2026-05-05', 'Paid'),
(2, 2, 550.00, 'May 2026', '2026-05-05', 'Paid'),
(3, 1, 500.00, 'May 2026', '2026-05-05', 'Unpaid'),
(4, 2, 550.00, 'May 2026', '2026-05-05', 'Paid'),
(5, 3, 450.00, 'May 2026', '2026-05-05', 'Partial'),
(6, 1, 500.00, 'May 2026', '2026-05-05', 'Paid'),
(7, 4, 600.00, 'May 2026', '2026-05-05', 'Unpaid'),
(8, 4, 600.00, 'May 2026', '2026-05-05', 'Paid');
GO

-- PAYMENTS
INSERT INTO payments (passenger_id, fee_id, amount, payment_date, payment_method, description) VALUES
(1, 1, 500.00, '2026-05-15', 'Cash', 'May transport fee'),
(2, 2, 550.00, '2026-05-12', 'M-Pesa', 'May transport fee'),
(4, 4, 550.00, '2026-05-18', 'Bank Transfer', 'May transport fee'),
(6, 6, 500.00, '2026-05-20', 'Cash', 'May transport fee'),
(8, 8, 600.00, '2026-05-22', 'M-Pesa', 'May transport fee'),
(3, NULL, 250.00, '2026-05-25', 'Cash', 'Partial payment'),
(5, NULL, 200.00, '2026-05-24', 'M-Pesa', 'Partial payment'),
(7, NULL, 300.00, '2026-05-21', 'Bank Transfer', 'Partial payment');
GO

-- FUEL LOGS
INSERT INTO fuel_logs (vehicle_id, log_date, liters, cost, odometer) VALUES
(1, '2026-05-28', 50.0, 4500.00, 15000),
(1, '2026-05-30', 45.0, 4050.00, 15150),
(2, '2026-05-27', 60.0, 5400.00, 8000),
(2, '2026-05-30', 55.0, 4950.00, 8200),
(4, '2026-05-26', 100.0, 9000.00, 45000),
(4, '2026-05-29', 90.0, 8100.00, 45500),
(5, '2026-05-25', 70.0, 6300.00, 12000),
(5, '2026-05-30', 65.0, 5850.00, 12350);
GO

-- MAINTENANCE RECORDS
INSERT INTO maintenance_records (vehicle_id, issue_description, reported_by_driver_id, status, scheduled_date, completed_date, cost) VALUES
(1, 'Regular oil change and filter replacement', 1, 'Completed', '2026-05-25', '2026-05-26', 2500.00),
(2, 'Brake pad replacement', 2, 'In Progress', '2026-05-28', NULL, 0.00),
(3, 'Engine overheating issue - needs diagnosis', 3, 'Reported', '2026-05-30', NULL, 0.00),
(4, 'Tire rotation and wheel alignment', 4, 'Completed', '2026-05-20', '2026-05-21', 3500.00),
(5, 'Air conditioning service', 5, 'Scheduled', '2026-06-02', NULL, 0.00),
(1, 'Windshield wiper replacement', 1, 'Completed', '2026-05-15', '2026-05-15', 800.00),
(2, 'Battery check and cleaning', 2, 'In Progress', '2026-05-29', NULL, 0.00);
GO

-- TRACKING LOGS (GPS Data)
INSERT INTO tracking_logs (schedule_id, latitude, longitude, timestamp, status) VALUES
(1, -1.286389, 36.817223, '2026-05-30 06:30:15', 'Departed'),
(1, -1.295389, 36.825223, '2026-05-30 06:35:30', 'In Transit'),
(1, -1.304389, 36.833223, '2026-05-30 06:40:45', 'In Transit'),
(1, -1.313389, 36.841223, '2026-05-30 06:45:00', 'Arrived'),
(2, -1.286389, 36.817223, '2026-05-30 08:00:30', 'Departed'),
(2, -1.290389, 36.820223, '2026-05-30 08:15:45', 'In Transit'),
(2, -1.294389, 36.823223, '2026-05-30 08:30:00', 'Arrived'),
(3, -1.286389, 36.817223, '2026-05-30 15:00:00', 'Departed'),
(3, -1.288389, 36.819223, '2026-05-30 15:05:15', 'In Transit'),
(4, -1.286389, 36.817223, '2026-05-30 07:00:30', 'Departed'),
(4, -1.305389, 36.835223, '2026-05-30 08:10:00', 'Arrived');
GO
