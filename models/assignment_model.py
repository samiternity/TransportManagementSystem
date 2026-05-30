from database.db_handler import DatabaseHandler

class AssignmentModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def _supports_monthly_fare(self):
        return self.db.execute_scalar(
            "SELECT COL_LENGTH('assignments', 'monthly_fare')"
        ) is not None

    def create_assignment(self, vehicle_id, driver_id, route_id, start_date, monthly_fare=500.0, end_date=None):
        if self._supports_monthly_fare():
            query = """
                INSERT INTO assignments (vehicle_id, driver_id, route_id, start_date, end_date, status, monthly_fare)
                VALUES (?, ?, ?, ?, ?, 'Active', ?)
            """
            insert_params = (vehicle_id, driver_id, route_id, start_date, end_date, monthly_fare)
        else:
            query = """
                INSERT INTO assignments (vehicle_id, driver_id, route_id, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?, 'Active')
            """
            insert_params = (vehicle_id, driver_id, route_id, start_date, end_date)

        # We use a transaction because we also want to update vehicle and driver status
        queries = [
            (query, insert_params),
            ("UPDATE vehicles SET status = 'In Service' WHERE id = ?", (vehicle_id,)),
            ("UPDATE drivers SET status = 'On Trip' WHERE id = ?", (driver_id,))
        ]
        return self.db.execute_transaction(queries)

    def get_active_assignments(self):
        if self._supports_monthly_fare():
            query = """
                SELECT a.id, v.plate_number, d.name, r.origin, r.destination, a.start_date, a.monthly_fare
                FROM assignments a
                JOIN vehicles v ON a.vehicle_id = v.id
                JOIN drivers d ON a.driver_id = d.id
                JOIN routes r ON a.route_id = r.id
                WHERE a.status = 'Active'
            """
        else:
            query = """
                SELECT a.id, v.plate_number, d.name, r.origin, r.destination, a.start_date, CAST(500.00 AS DECIMAL(10,2)) AS monthly_fare
                FROM assignments a
                JOIN vehicles v ON a.vehicle_id = v.id
                JOIN drivers d ON a.driver_id = d.id
                JOIN routes r ON a.route_id = r.id
                WHERE a.status = 'Active'
            """
        return self.db.execute_query(query, fetch=True)

    def get_assignment_details(self, assignment_id):
        if self._supports_monthly_fare():
            query = """
                SELECT a.id, v.id, d.id, r.id, v.capacity, a.status, a.monthly_fare
                FROM assignments a
                JOIN vehicles v ON a.vehicle_id = v.id
                JOIN drivers d ON a.driver_id = d.id
                JOIN routes r ON a.route_id = r.id
                WHERE a.id = ?
            """
        else:
            query = """
                SELECT a.id, v.id, d.id, r.id, v.capacity, a.status, CAST(500.00 AS DECIMAL(10,2)) AS monthly_fare
                FROM assignments a
                JOIN vehicles v ON a.vehicle_id = v.id
                JOIN drivers d ON a.driver_id = d.id
                JOIN routes r ON a.route_id = r.id
                WHERE a.id = ?
            """
        results = self.db.execute_query(query, (assignment_id,), fetch=True)
        return results[0] if results else None
