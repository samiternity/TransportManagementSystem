from database.db_handler import DatabaseHandler

class VehicleModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def get_all(self):
        query = "SELECT id, plate_number, make, model, year, capacity, status, mileage, fuel_type FROM vehicles"
        return self.db.execute_query(query, fetch=True)

    def get_by_id(self, vehicle_id):
        query = "SELECT id, plate_number, make, model, year, capacity, status, mileage, fuel_type FROM vehicles WHERE id = ?"
        results = self.db.execute_query(query, (vehicle_id,), fetch=True)
        return results[0] if results else None

    def get_available(self):
        query = "SELECT id, plate_number, make, model, capacity FROM vehicles WHERE status = 'Available'"
        return self.db.execute_query(query, fetch=True)

    def create(self, plate, make, model, year, capacity, status, mileage, fuel_type):
        query = """
            INSERT INTO vehicles (plate_number, make, model, year, capacity, status, mileage, fuel_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (plate, make, model, year, capacity, status, mileage, fuel_type))

    def update(self, v_id, plate, make, model, year, capacity, status, mileage, fuel_type):
        query = """
            UPDATE vehicles 
            SET plate_number=?, make=?, model=?, year=?, capacity=?, status=?, mileage=?, fuel_type=?
            WHERE id=?
        """
        return self.db.execute_query(query, (plate, make, model, year, capacity, status, mileage, fuel_type, v_id))

    def delete(self, v_id):
        query = "DELETE FROM vehicles WHERE id = ?"
        return self.db.execute_query(query, (v_id,))

    def update_status(self, v_id, status):
        query = "UPDATE vehicles SET status = ? WHERE id = ?"
        return self.db.execute_query(query, (status, v_id))
