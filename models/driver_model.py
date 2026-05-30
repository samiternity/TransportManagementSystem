from database.db_handler import DatabaseHandler

class DriverModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def get_all(self):
        query = "SELECT id, name, license_number, phone, status, assigned_vehicle_id FROM drivers"
        return self.db.execute_query(query, fetch=True)

    def get_available(self):
        query = "SELECT id, name, license_number FROM drivers WHERE status = 'Available'"
        return self.db.execute_query(query, fetch=True)

    def create(self, name, license_number, phone, status, assigned_vehicle_id):
        query = "INSERT INTO drivers (name, license_number, phone, status, assigned_vehicle_id) VALUES (?, ?, ?, ?, ?)"
        return self.db.execute_query(query, (name, license_number, phone, status, assigned_vehicle_id))

    def update(self, d_id, name, license_number, phone, status, assigned_vehicle_id):
        query = "UPDATE drivers SET name=?, license_number=?, phone=?, status=?, assigned_vehicle_id=? WHERE id=?"
        return self.db.execute_query(query, (name, license_number, phone, status, assigned_vehicle_id, d_id))

    def delete(self, d_id):
        query = "DELETE FROM drivers WHERE id = ?"
        return self.db.execute_query(query, (d_id,))

    def update_status(self, d_id, status):
        query = "UPDATE drivers SET status = ? WHERE id = ?"
        return self.db.execute_query(query, (status, d_id))
