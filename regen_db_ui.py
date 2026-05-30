from pathlib import Path
from textwrap import dedent

files = {
    'database/schema.sql': dedent('''
        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[users]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[users] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(100) NOT NULL UNIQUE,
                password_hash NVARCHAR(255) NOT NULL,
                role NVARCHAR(50) NOT NULL
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[drivers]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[drivers] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(150) NOT NULL,
                license_number NVARCHAR(100) NOT NULL,
                phone NVARCHAR(50),
                status NVARCHAR(50) NOT NULL,
                assigned_vehicle_id INT NULL
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[vehicles]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[vehicles] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                plate_number NVARCHAR(50) NOT NULL UNIQUE,
                make NVARCHAR(100) NOT NULL,
                model NVARCHAR(100) NOT NULL,
                year INT NOT NULL,
                status NVARCHAR(50) NOT NULL,
                mileage INT NOT NULL
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[routes]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[routes] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                origin NVARCHAR(100) NOT NULL,
                destination NVARCHAR(100) NOT NULL,
                distance_km DECIMAL(6,2) NOT NULL,
                duration_minutes INT NOT NULL
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[schedules]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[schedules] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                route_id INT NOT NULL,
                vehicle_id INT NOT NULL,
                driver_id INT NOT NULL,
                departure_time DATETIME NOT NULL,
                arrival_time DATETIME NOT NULL,
                status NVARCHAR(50) NOT NULL,
                FOREIGN KEY (route_id) REFERENCES routes(id),
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (driver_id) REFERENCES drivers(id)
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[fuel_logs]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[fuel_logs] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                vehicle_id INT NOT NULL,
                log_date DATETIME NOT NULL,
                liters DECIMAL(8,2) NOT NULL,
                cost DECIMAL(10,2) NOT NULL,
                odometer INT NOT NULL,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[maintenance_records]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[maintenance_records] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                vehicle_id INT NOT NULL,
                issue NVARCHAR(250) NOT NULL,
                status NVARCHAR(50) NOT NULL,
                scheduled_date DATETIME NULL,
                completed_date DATETIME NULL,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[payments]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[payments] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                passenger_name NVARCHAR(150) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                payment_date DATETIME NOT NULL,
                description NVARCHAR(250) NOT NULL
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[tracking_records]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[tracking_records] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                schedule_id INT NOT NULL,
                latitude DECIMAL(9,6) NOT NULL,
                longitude DECIMAL(9,6) NOT NULL,
                timestamp DATETIME NOT NULL,
                status NVARCHAR(50) NOT NULL,
                FOREIGN KEY (schedule_id) REFERENCES schedules(id)
            );
        END
        GO

        IF NOT EXISTS (
            SELECT 1 FROM sys.objects
            WHERE object_id = OBJECT_ID(N'[dbo].[bookings]')
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE [dbo].[bookings] (
                id INT IDENTITY(1,1) PRIMARY KEY,
                passenger_name NVARCHAR(150) NOT NULL,
                route_id INT NOT NULL,
                schedule_id INT NOT NULL,
                booking_date DATETIME NOT NULL,
                status NVARCHAR(50) NOT NULL,
                FOREIGN KEY (route_id) REFERENCES routes(id),
                FOREIGN KEY (schedule_id) REFERENCES schedules(id)
            );
        END
        GO
    ''').lstrip(),
    'setup_database.py': dedent('''
        import re
        import pyodbc

        from config import (
            MSSQL_DATABASE,
            MSSQL_DRIVER,
            MSSQL_SERVER,
            MSSQL_TRUSTED_CONNECTION,
            MSSQL_USERNAME,
            MSSQL_PASSWORD,
            build_connection_string,
        )


        def build_master_connection_string() -> str:
            parts = [
                f'DRIVER={{{MSSQL_DRIVER}}}',
                f'SERVER={MSSQL_SERVER}',
                'DATABASE=master',
                'Encrypt=no',
                'TrustServerCertificate=yes',
            ]
            if MSSQL_TRUSTED_CONNECTION:
                parts.append('Trusted_Connection=yes')
            else:
                parts.append(f'UID={MSSQL_USERNAME}')
                parts.append(f'PWD={MSSQL_PASSWORD}')
            return ';'.join(parts) + ';'


        def get_master_connection():
            return pyodbc.connect(build_master_connection_string(), autocommit=True)


        def create_database_if_missing():
            with get_master_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"IF DB_ID(N'{MSSQL_DATABASE}') IS NULL CREATE DATABASE [{MSSQL_DATABASE}]"
                )
                cursor.close()


        def split_batches(sql_text: str):
            return [batch.strip() for batch in re.split(r'^\\s*GO\\s*$', sql_text, flags=re.MULTILINE | re.IGNORECASE) if batch.strip()]


        def create_schema():
            with open('database/schema.sql', 'r', encoding='utf-8') as file:
                schema_sql = file.read()
            with pyodbc.connect(build_connection_string(), autocommit=False) as conn:
                cursor = conn.cursor()
                for batch in split_batches(schema_sql):
                    cursor.execute(batch)
                conn.commit()
                cursor.close()


        def seed_data():
            with pyodbc.connect(build_connection_string(), autocommit=False) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(1) FROM users")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 'admin', 'Pass@123', 'Administrator')
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 'driver01', 'Pass@123', 'Driver')
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 'student01', 'Pass@123', 'Passenger')
                    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 'maint01', 'Pass@123', 'Maintenance')

                cursor.execute("SELECT COUNT(1) FROM drivers")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO drivers (name, license_number, phone, status, assigned_vehicle_id) VALUES (?, ?, ?, ?, ?)",
                        [
                            ('Ahmed Khan', 'DR-001', '+92 300 1112223', 'Active', 1),
                            ('Sara Ali', 'DR-002', '+92 300 1112224', 'Active', 2),
                            ('Bilal Raza', 'DR-003', '+92 300 1112225', 'Suspended', 3),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM vehicles")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO vehicles (plate_number, make, model, year, status, mileage) VALUES (?, ?, ?, ?, ?, ?)",
                        [
                            ('ABC-1234', 'Toyota', 'HiAce', 2020, 'Ready', 135000),
                            ('DEF-5678', 'Suzuki', 'Ravi', 2018, 'In Service', 98000),
                            ('GHI-9012', 'Honda', 'Civic', 2019, 'Ready', 112500),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM routes")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO routes (origin, destination, distance_km, duration_minutes) VALUES (?, ?, ?, ?)",
                        [
                            ('Islamabad', 'Peshawar', 180.50, 210),
                            ('Lahore', 'Islamabad', 380.00, 360),
                            ('Karachi', 'Hyderabad', 165.00, 180),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM schedules")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO schedules (route_id, vehicle_id, driver_id, departure_time, arrival_time, status) VALUES (?, ?, ?, ?, ?, ?)",
                        [
                            (1, 1, 1, '2026-05-06 08:00:00', '2026-05-06 11:30:00', 'On Time'),
                            (2, 2, 2, '2026-05-06 09:00:00', '2026-05-06 15:00:00', 'Delayed'),
                            (3, 3, 3, '2026-05-07 10:00:00', '2026-05-07 13:00:00', 'Scheduled'),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM fuel_logs")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO fuel_logs (vehicle_id, log_date, liters, cost, odometer) VALUES (?, ?, ?, ?, ?)",
                        [
                            (1, '2026-05-01 07:30:00', 60.5, 13200.00, 134500),
                            (2, '2026-05-02 10:15:00', 45.0, 9900.00, 97900),
                            (3, '2026-05-02 12:00:00', 55.0, 12100.00, 112400),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM maintenance_records")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO maintenance_records (vehicle_id, issue, status, scheduled_date, completed_date) VALUES (?, ?, ?, ?, ?)",
                        [
                            (2, 'Brake pad replacement', 'In Progress', '2026-05-10 09:00:00', NULL),
                            (3, 'AC compressor service', 'Scheduled', '2026-05-12 11:00:00', NULL),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM payments")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO payments (passenger_name, amount, payment_date, description) VALUES (?, ?, ?, ?)",
                        [
                            ('student01', 1500.00, '2026-05-01 14:00:00', 'Islamabad - Peshawar ticket'),
                            ('student01', 2200.00, '2026-05-03 11:30:00', 'Lahore - Islamabad ticket'),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM bookings")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO bookings (passenger_name, route_id, schedule_id, booking_date, status) VALUES (?, ?, ?, ?, ?)",
                        [
                            ('student01', 1, 1, '2026-05-01 13:30:00', 'Confirmed'),
                            ('student01', 2, 2, '2026-05-02 10:45:00', 'Confirmed'),
                        ],
                    )

                cursor.execute("SELECT COUNT(1) FROM tracking_records")
                if cursor.fetchone()[0] == 0:
                    cursor.executemany(
                        "INSERT INTO tracking_records (schedule_id, latitude, longitude, timestamp, status) VALUES (?, ?, ?, ?, ?)",
                        [
                            (1, 33.6844, 73.0479, '2026-05-06 09:30:00', 'En Route'),
                            (2, 31.5204, 74.3587, '2026-05-06 12:00:00', 'Delayed'),
                        ],
                    )

                conn.commit()
                cursor.close()


        def main():
            print('Creating SQL Server database if needed...')
            create_database_if_missing()
            print('Creating schema...')
            create_schema()
            print('Seeding sample data...')
            seed_data()
            print(f'SQL Server database ready: {MSSQL_DATABASE}')


        if __name__ == '__main__':
            main()
    ''').lstrip(),
    'models/driver_model.py': dedent('''
        from database.connection import get_connection


        def get_all_drivers():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, name, license_number, phone, status, assigned_vehicle_id FROM drivers',
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/vehicle_model.py': dedent('''
        from database.connection import get_connection


        def get_all_vehicles():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, plate_number, make, model, year, status, mileage FROM vehicles',
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/route_model.py': dedent('''
        from database.connection import get_connection


        def get_all_routes():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, origin, destination, distance_km, duration_minutes FROM routes',
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/schedule_model.py': dedent('''
        from database.connection import get_connection


        def get_all_schedules():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        s.id,
                        r.origin,
                        r.destination,
                        v.plate_number,
                        d.name,
                        s.departure_time,
                        s.arrival_time,
                        s.status
                    FROM schedules s
                    LEFT JOIN routes r ON s.route_id = r.id
                    LEFT JOIN vehicles v ON s.vehicle_id = v.id
                    LEFT JOIN drivers d ON s.driver_id = d.id
                    """,
                )
                return cursor.fetchall()


        def get_schedules_for_driver(driver_id):
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        s.id,
                        r.origin,
                        r.destination,
                        v.plate_number,
                        s.departure_time,
                        s.arrival_time,
                        s.status
                    FROM schedules s
                    LEFT JOIN routes r ON s.route_id = r.id
                    LEFT JOIN vehicles v ON s.vehicle_id = v.id
                    WHERE s.driver_id = ?
                    """,
                    driver_id,
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/fuel_model.py': dedent('''
        from database.connection import get_connection


        def get_fuel_logs():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT f.id, v.plate_number, f.log_date, f.liters, f.cost, f.odometer
                    FROM fuel_logs f
                    LEFT JOIN vehicles v ON f.vehicle_id = v.id
                    ORDER BY f.log_date DESC
                    """,
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/maintenance_model.py': dedent('''
        from database.connection import get_connection


        def get_maintenance_records():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT m.id, v.plate_number, m.issue, m.status, m.scheduled_date, m.completed_date
                    FROM maintenance_records m
                    LEFT JOIN vehicles v ON m.vehicle_id = v.id
                    ORDER BY m.id DESC
                    """,
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/payment_model.py': dedent('''
        from database.connection import get_connection


        def get_payments_for_passenger(passenger_name):
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, amount, payment_date, description FROM payments WHERE passenger_name = ? ORDER BY payment_date DESC',
                    passenger_name,
                )
                return cursor.fetchall()


        def get_all_payments():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, passenger_name, amount, payment_date, description FROM payments ORDER BY payment_date DESC')
                return cursor.fetchall()
    ''').lstrip(),
    'models/tracking_model.py': dedent('''
        from database.connection import get_connection


        def get_tracking_records():
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT t.id, s.id, t.latitude, t.longitude, t.timestamp, t.status
                    FROM tracking_records t
                    LEFT JOIN schedules s ON t.schedule_id = s.id
                    ORDER BY t.timestamp DESC
                    """,
                )
                return cursor.fetchall()
    ''').lstrip(),
    'models/passenger_model.py': dedent('''
        from database.connection import get_connection


        def get_bookings_for_passenger(passenger_name):
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT b.id, r.origin, r.destination, s.departure_time, s.arrival_time, b.status
                    FROM bookings b
                    LEFT JOIN routes r ON b.route_id = r.id
                    LEFT JOIN schedules s ON b.schedule_id = s.id
                    WHERE b.passenger_name = ?
                    ORDER BY b.booking_date DESC
                    """,
                    passenger_name,
                )
                return cursor.fetchall()
    ''').lstrip(),
    'controllers/auth_controller.py': dedent('''
        from models.user_model import UserModel


        def login(username, password):
            return UserModel.authenticate(username, password)
    ''').lstrip(),
    'controllers/driver_controller.py': dedent('''
        from models.driver_model import get_all_drivers


        def list_drivers():
            return get_all_drivers()
    ''').lstrip(),
    'controllers/vehicle_controller.py': dedent('''
        from models.vehicle_model import get_all_vehicles


        def list_vehicles():
            return get_all_vehicles()
    ''').lstrip(),
    'controllers/route_controller.py': dedent('''
        from models.route_model import get_all_routes


        def list_routes():
            return get_all_routes()
    ''').lstrip(),
    'controllers/schedule_controller.py': dedent('''
        from models.schedule_model import get_all_schedules, get_schedules_for_driver


        def list_schedules():
            return get_all_schedules()


        def list_schedules_for_driver(driver_id):
            return get_schedules_for_driver(driver_id)
    ''').lstrip(),
    'controllers/fuel_controller.py': dedent('''
        from models.fuel_model import get_fuel_logs


        def list_fuel_logs():
            return get_fuel_logs()
    ''').lstrip(),
    'controllers/maintenance_controller.py': dedent('''
        from models.maintenance_model import get_maintenance_records


        def list_maintenance_records():
            return get_maintenance_records()
    ''').lstrip(),
    'controllers/payment_controller.py': dedent('''
        from models.payment_model import get_all_payments, get_payments_for_passenger


        def list_payments():
            return get_all_payments()


        def payments_for_passenger(passenger_name):
            return get_payments_for_passenger(passenger_name)
    ''').lstrip(),
    'controllers/tracking_controller.py': dedent('''
        from models.tracking_model import get_tracking_records


        def list_tracking_records():
            return get_tracking_records()
    ''').lstrip(),
    'controllers/passenger_controller.py': dedent('''
        from models.passenger_model import get_bookings_for_passenger


        def list_bookings_for_passenger(name):
            return get_bookings_for_passenger(name)
    ''').lstrip(),
    'views/common.py': dedent('''
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QLabel,
            QTableWidget,
            QTableWidgetItem,
            QHeaderView,
        )
        from PyQt5.QtCore import Qt


        class TablePage(QWidget):
            def __init__(self, title, description, columns, rows):
                super().__init__()
                self.setObjectName(title.replace(' ', '_'))
                self.setMinimumSize(640, 420)
                layout = QVBoxLayout()
                header = QLabel(title)
                header.setStyleSheet('font-size: 20px; font-weight: bold;')
                subtitle = QLabel(description)
                subtitle.setWordWrap(True)
                subtitle.setStyleSheet('color: #555; margin-bottom: 12px;')
                layout.addWidget(header)
                layout.addWidget(subtitle)

                table = QTableWidget(len(rows), len(columns))
                table.setHorizontalHeaderLabels(columns)
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                table.verticalHeader().setVisible(False)
                table.setEditTriggers(QTableWidget.NoEditTriggers)
                table.setSelectionBehavior(QTableWidget.SelectRows)
                table.setSelectionMode(QTableWidget.SingleSelection)
                table.setAlternatingRowColors(True)
                for row_index, row_values in enumerate(rows):
                    for col_index, value in enumerate(row_values):
                        item = QTableWidgetItem(str(value) if value is not None else '')
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(row_index, col_index, item)

                layout.addWidget(table)
                self.setLayout(layout)
    ''').lstrip(),
    'views/admin/dashboard.py': dedent('''
        from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame
        from controllers.vehicle_controller import list_vehicles
        from controllers.driver_controller import list_drivers
        from controllers.route_controller import list_routes
        from controllers.schedule_controller import list_schedules
        from controllers.fuel_controller import list_fuel_logs
        from controllers.maintenance_controller import list_maintenance_records
        from controllers.payment_controller import list_payments
        from controllers.tracking_controller import list_tracking_records
        from controllers.passenger_controller import list_bookings_for_passenger


        class AdminDashboardPage(QWidget):
            def __init__(self):
                super().__init__()
                self.setObjectName('AdminDashboardPage')
                main_layout = QVBoxLayout()
                title = QLabel('Admin Dashboard')
                title.setStyleSheet('font-size: 20px; font-weight: bold;')
                subtitle = QLabel('Quick overview of the transport management system.')
                subtitle.setStyleSheet('color: #555; margin-bottom: 18px;')
                subtitle.setWordWrap(True)

                stats = [
                    ('Vehicles', len(list_vehicles())),
                    ('Drivers', len(list_drivers())),
                    ('Routes', len(list_routes())),
                    ('Schedules', len(list_schedules())),
                    ('Fuel Logs', len(list_fuel_logs())),
                    ('Maintenance Tasks', len(list_maintenance_records())),
                    ('Payments', len(list_payments())),
                    ('Tracking Records', len(list_tracking_records())),
                ]

                grid = QWidget()
                grid_layout = QHBoxLayout()
                grid_layout.setSpacing(16)
                for label_text, value in stats:
                    card = QFrame()
                    card.setStyleSheet('background: #ffffff; border: 1px solid #dcdcdc; border-radius: 10px; padding: 16px;')
                    card_layout = QVBoxLayout()
                    card_label = QLabel(label_text)
                    card_label.setStyleSheet('font-size: 14px; color: #333;')
                    card_value = QLabel(str(value))
                    card_value.setStyleSheet('font-size: 22px; font-weight: bold;')
                    card_layout.addWidget(card_label)
                    card_layout.addWidget(card_value)
                    card.setLayout(card_layout)
                    grid_layout.addWidget(card)
                grid.setLayout(grid_layout)

                main_layout.addWidget(title)
                main_layout.addWidget(subtitle)
                main_layout.addWidget(grid)
                main_layout.addStretch(1)
                self.setLayout(main_layout)
    ''').lstrip(),
    'views/admin/vehicle_management.py': dedent('''
        from views.common import TablePage
        from controllers.vehicle_controller import list_vehicles


        class VehicleManagementPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Plate', 'Make', 'Model', 'Year', 'Status', 'Mileage']
                rows = list_vehicles()
                super().__init__('Vehicle Management', 'Browse and monitor fleet status.', columns, rows)
    ''').lstrip(),
    'views/admin/driver_management.py': dedent('''
        from views.common import TablePage
        from controllers.driver_controller import list_drivers


        class DriverManagementPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Name', 'License', 'Phone', 'Status', 'Vehicle ID']
                rows = list_drivers()
                super().__init__('Driver Management', 'View driver assignments and contact details.', columns, rows)
    ''').lstrip(),
    'views/admin/route_management.py': dedent('''
        from views.common import TablePage
        from controllers.route_controller import list_routes


        class RouteManagementPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Origin', 'Destination', 'Distance (km)', 'Duration (min)']
                rows = list_routes()
                super().__init__('Route Management', 'Manage route schedules and distances.', columns, rows)
    ''').lstrip(),
    'views/admin/schedule_management.py': dedent('''
        from views.common import TablePage
        from controllers.schedule_controller import list_schedules


        class ScheduleManagementPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Origin', 'Destination', 'Vehicle', 'Driver', 'Departure', 'Arrival', 'Status']
                rows = list_schedules()
                super().__init__('Schedule Management', 'Track schedule assignments and status.', columns, rows)
    ''').lstrip(),
    'views/admin/fuel_management.py': dedent('''
        from views.common import TablePage
        from controllers.fuel_controller import list_fuel_logs


        class FuelManagementPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Vehicle', 'Date', 'Liters', 'Cost', 'Odometer']
                rows = list_fuel_logs()
                super().__init__('Fuel Management', 'Monitor fuel usage and refill history.', columns, rows)
    ''').lstrip(),
    'views/admin/maintenance_panel.py': dedent('''
        from views.common import TablePage
        from controllers.maintenance_controller import list_maintenance_records


        class MaintenancePanelPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
                rows = list_maintenance_records()
                super().__init__('Maintenance Panel', 'Review maintenance work orders and status.', columns, rows)
    ''').lstrip(),
    'views/admin/billing_management.py': dedent('''
        from views.common import TablePage
        from controllers.payment_controller import list_payments


        class BillingManagementPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Passenger', 'Amount', 'Date', 'Description']
                rows = list_payments()
                super().__init__('Billing Management', 'Review payment transactions and receipts.', columns, rows)
    ''').lstrip(),
    'views/admin/reports.py': dedent('''
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
        from controllers.vehicle_controller import list_vehicles
        from controllers.driver_controller import list_drivers
        from controllers.route_controller import list_routes
        from controllers.schedule_controller import list_schedules
        from controllers.payment_controller import list_payments


        class ReportsPage(QWidget):
            def __init__(self):
                super().__init__()
                self.setObjectName('ReportsPage')
                layout = QVBoxLayout()
                title = QLabel('Reports')
                title.setStyleSheet('font-size: 20px; font-weight: bold;')
                description = QLabel('View key performance metrics and system summaries.')
                description.setStyleSheet('color: #555; margin-bottom: 18px;')
                description.setWordWrap(True)

                text = f"""
                Vehicles: {len(list_vehicles())}\n
                Drivers: {len(list_drivers())}\n
                Routes: {len(list_routes())}\n
                Schedule entries: {len(list_schedules())}\n
                Payments recorded: {len(list_payments())}
                """
                details = QLabel(text)
                details.setStyleSheet('font-size: 14px; color: #333;')
                details.setWordWrap(True)

                layout.addWidget(title)
                layout.addWidget(description)
                layout.addWidget(details)
                layout.addStretch(1)
                self.setLayout(layout)
    ''').lstrip(),
    'views/admin/tracking_panel.py': dedent('''
        from views.common import TablePage
        from controllers.tracking_controller import list_tracking_records


        class TrackingPanelPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Schedule ID', 'Latitude', 'Longitude', 'Timestamp', 'Status']
                rows = list_tracking_records()
                super().__init__('Tracking Panel', 'Monitor vehicle location updates and trip progress.', columns, rows)
    ''').lstrip(),
    'views/driver/driver_dashboard.py': dedent('''
        from views.common import TablePage
        from controllers.schedule_controller import list_schedules


        class DriverDashboardPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Origin', 'Destination', 'Vehicle', 'Driver', 'Departure', 'Arrival', 'Status']
                rows = list_schedules()
                super().__init__('Driver Dashboard', 'See assigned schedules and current trip status.', columns, rows)
    ''').lstrip(),
    'views/driver/trip_status.py': dedent('''
        from views.common import TablePage
        from controllers.schedule_controller import list_schedules


        class TripStatusPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Origin', 'Destination', 'Vehicle', 'Driver', 'Departure', 'Arrival', 'Status']
                rows = list_schedules()
                super().__init__('Trip Status', 'Check the status of current and upcoming trips.', columns, rows)
    ''').lstrip(),
    'views/driver/report_issue.py': dedent('''
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


        class ReportIssuePage(QWidget):
            def __init__(self):
                super().__init__()
                self.setObjectName('ReportIssuePage')
                layout = QVBoxLayout()
                title = QLabel('Report Issue')
                title.setStyleSheet('font-size: 20px; font-weight: bold;')
                description = QLabel('Submit a vehicle or route issue to maintenance. This page is wired to the database pipeline for future issue reporting.')
                description.setWordWrap(True)
                description.setStyleSheet('color: #555;')

                layout.addWidget(title)
                layout.addWidget(description)
                layout.addStretch(1)
                self.setLayout(layout)
    ''').lstrip(),
    'views/maintenance/maintenance_dashboard.py': dedent('''
        from views.common import TablePage
        from controllers.maintenance_controller import list_maintenance_records


        class MaintenanceDashboardPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
                rows = list_maintenance_records()
                super().__init__('Maintenance Dashboard', 'Review maintenance work orders and vehicle inspection tasks.', columns, rows)
    ''').lstrip(),
    'views/maintenance/repair_scheduler.py': dedent('''
        from views.common import TablePage
        from controllers.maintenance_controller import list_maintenance_records


        class RepairSchedulerPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
                rows = list_maintenance_records()
                super().__init__('Repair Scheduler', 'Schedule repairs and track maintenance timelines.', columns, rows)
    ''').lstrip(),
    'views/maintenance/vehicle_inspection.py': dedent('''
        from views.common import TablePage
        from controllers.maintenance_controller import list_maintenance_records


        class VehicleInspectionPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
                rows = list_maintenance_records()
                super().__init__('Vehicle Inspection', 'Inspect vehicles and verify service completion.', columns, rows)
    ''').lstrip(),
    'views/passenger/passenger_dashboard.py': dedent('''
        from views.common import TablePage
        from controllers.passenger_controller import list_bookings_for_passenger


        class PassengerDashboardPage(TablePage):
            def __init__(self):
                columns = ['Booking ID', 'Origin', 'Destination', 'Departure', 'Arrival', 'Status']
                rows = list_bookings_for_passenger('student01')
                super().__init__('Passenger Dashboard', 'View your bookings and upcoming trips.', columns, rows)
    ''').lstrip(),
    'views/passenger/book_transport.py': dedent('''
        from views.common import TablePage
        from controllers.route_controller import list_routes


        class BookTransportPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Origin', 'Destination', 'Distance (km)', 'Duration (min)']
                rows = list_routes()
                super().__init__('Book Transport', 'Browse routes and select a trip for booking.', columns, rows)
    ''').lstrip(),
    'views/passenger/payment_history.py': dedent('''
        from views.common import TablePage
        from controllers.payment_controller import payments_for_passenger


        class PaymentHistoryPage(TablePage):
            def __init__(self):
                columns = ['ID', 'Amount', 'Date', 'Description']
                rows = payments_for_passenger('student01')
                super().__init__('Payment History', 'View your transaction history and receipts.', columns, rows)
    ''').lstrip(),
}

for filepath, content in files.items():
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f'Wrote {filepath}')
