-- =============================================================================
-- database/schema.sql
-- Transport Management System - Enterprise Refactor (Drop and Recreate)
-- =============================================================================

-- Drop in strict reverse dependency order
IF OBJECT_ID(N'[dbo].[audit_logs]', 'U') IS NOT NULL DROP TABLE [dbo].[audit_logs];
IF OBJECT_ID(N'[dbo].[stops]', 'U') IS NOT NULL DROP TABLE [dbo].[stops];
IF OBJECT_ID(N'[dbo].[tracking_logs]', 'U') IS NOT NULL DROP TABLE [dbo].[tracking_logs];
IF OBJECT_ID(N'[dbo].[tracking_records]', 'U') IS NOT NULL DROP TABLE [dbo].[tracking_records];
IF OBJECT_ID(N'[dbo].[payments]', 'U') IS NOT NULL DROP TABLE [dbo].[payments];
IF OBJECT_ID(N'[dbo].[transport_fees]', 'U') IS NOT NULL DROP TABLE [dbo].[transport_fees];
IF OBJECT_ID(N'[dbo].[bookings]', 'U') IS NOT NULL DROP TABLE [dbo].[bookings];
IF OBJECT_ID(N'[dbo].[schedules]', 'U') IS NOT NULL DROP TABLE [dbo].[schedules];
IF OBJECT_ID(N'[dbo].[maintenance_records]', 'U') IS NOT NULL DROP TABLE [dbo].[maintenance_records];
IF OBJECT_ID(N'[dbo].[fuel_logs]', 'U') IS NOT NULL DROP TABLE [dbo].[fuel_logs];
IF OBJECT_ID(N'[dbo].[assignments]', 'U') IS NOT NULL DROP TABLE [dbo].[assignments];
IF OBJECT_ID(N'[dbo].[passengers]', 'U') IS NOT NULL DROP TABLE [dbo].[passengers];
IF OBJECT_ID(N'[dbo].[drivers]', 'U') IS NOT NULL DROP TABLE [dbo].[drivers];
IF OBJECT_ID(N'[dbo].[routes]', 'U') IS NOT NULL DROP TABLE [dbo].[routes];
IF OBJECT_ID(N'[dbo].[vehicles]', 'U') IS NOT NULL DROP TABLE [dbo].[vehicles];
IF OBJECT_ID(N'[dbo].[users]', 'U') IS NOT NULL DROP TABLE [dbo].[users];
GO

-- 1. Users & Auth
CREATE TABLE [dbo].[users] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL
);
GO

-- 2. Vehicles
CREATE TABLE [dbo].[vehicles] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    plate_number NVARCHAR(50) NOT NULL UNIQUE,
    make NVARCHAR(100) NOT NULL,
    model NVARCHAR(100) NOT NULL,
    year INT NOT NULL,
    capacity INT NOT NULL DEFAULT 4,
    status NVARCHAR(50) NOT NULL DEFAULT 'Available',
    mileage INT NOT NULL DEFAULT 0,
    fuel_type NVARCHAR(50) DEFAULT 'Petrol'
);
GO

-- 3. Drivers
CREATE TABLE [dbo].[drivers] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    name NVARCHAR(150) NOT NULL,
    license_number NVARCHAR(100) NOT NULL UNIQUE,
    phone NVARCHAR(50),
    status NVARCHAR(50) NOT NULL DEFAULT 'Available',
    assigned_vehicle_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_vehicle_id) REFERENCES vehicles(id)
);
GO

-- 4. Routes
CREATE TABLE [dbo].[routes] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    origin NVARCHAR(100) NOT NULL,
    destination NVARCHAR(100) NOT NULL,
    distance_km DECIMAL(10,2) NOT NULL,
    duration_minutes INT NOT NULL,
    status NVARCHAR(50) DEFAULT 'Active'
);
GO

-- 5. Assignments
CREATE TABLE [dbo].[assignments] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    route_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    status NVARCHAR(50) DEFAULT 'Active',
    monthly_fare DECIMAL(15,2) NOT NULL DEFAULT 500.00,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (route_id) REFERENCES routes(id)
);
GO

-- 6. Schedules
CREATE TABLE [dbo].[schedules] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    assignment_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'Scheduled',
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);
GO

-- 7. Passengers
CREATE TABLE [dbo].[passengers] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    name NVARCHAR(150) NOT NULL,
    phone NVARCHAR(50),
    outstanding_balance DECIMAL(15,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
GO

-- 8. Bookings
CREATE TABLE [dbo].[bookings] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    passenger_id INT NOT NULL,
    assignment_id INT NOT NULL,
    booking_date DATETIME DEFAULT GETDATE(),
    status NVARCHAR(50) NOT NULL DEFAULT 'Confirmed',
    FOREIGN KEY (passenger_id) REFERENCES passengers(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);
GO

-- 9. Transport Fees
CREATE TABLE [dbo].[transport_fees] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    passenger_id INT NOT NULL,
    assignment_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    month_year NVARCHAR(20) NOT NULL,
    due_date DATE NOT NULL,
    status NVARCHAR(50) DEFAULT 'Unpaid',
    FOREIGN KEY (passenger_id) REFERENCES passengers(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);
GO

-- 10. Payments
CREATE TABLE [dbo].[payments] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    passenger_id INT NOT NULL,
    fee_id INT NULL,
    amount DECIMAL(15,2) NOT NULL,
    payment_date DATETIME DEFAULT GETDATE(),
    payment_method NVARCHAR(50) DEFAULT 'Cash',
    description NVARCHAR(250),
    FOREIGN KEY (passenger_id) REFERENCES passengers(id),
    FOREIGN KEY (fee_id) REFERENCES transport_fees(id)
);
GO

-- 11. Fuel Logs
CREATE TABLE [dbo].[fuel_logs] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    vehicle_id INT NOT NULL,
    log_date DATETIME DEFAULT GETDATE(),
    liters DECIMAL(10,2) NOT NULL,
    cost DECIMAL(15,2) NOT NULL,
    odometer INT NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
GO

-- 12. Maintenance Records
CREATE TABLE [dbo].[maintenance_records] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    vehicle_id INT NOT NULL,
    issue_description NVARCHAR(MAX) NOT NULL,
    reported_by_driver_id INT NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'Reported',
    scheduled_date DATETIME NULL,
    completed_date DATETIME NULL,
    cost DECIMAL(15,2) DEFAULT 0.00,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (reported_by_driver_id) REFERENCES drivers(id)
);
GO

-- 13. Tracking Logs
CREATE TABLE [dbo].[tracking_logs] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    schedule_id INT NOT NULL,
    latitude DECIMAL(11,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    timestamp DATETIME DEFAULT GETDATE(),
    status NVARCHAR(100),
    FOREIGN KEY (schedule_id) REFERENCES schedules(id)
);
GO

