from database.db_handler import DatabaseHandler

class RouteModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def get_all(self):
        query = "SELECT id, origin, destination, distance_km, duration_minutes, status FROM routes"
        return self.db.execute_query(query, fetch=True)

    def get_active(self):
        query = "SELECT id, origin, destination FROM routes WHERE status = 'Active'"
        return self.db.execute_query(query, fetch=True)

    def create(self, origin, destination, distance, duration):
        query = "INSERT INTO routes (origin, destination, distance_km, duration_minutes, status) VALUES (?, ?, ?, ?, 'Active')"
        return self.db.execute_query(query, (origin, destination, distance, duration))

    def update(self, r_id, origin, destination, distance, duration, status):
        query = "UPDATE routes SET origin=?, destination=?, distance_km=?, duration_minutes=?, status=? WHERE id=?"
        return self.db.execute_query(query, (origin, destination, distance, duration, status, r_id))

    def delete(self, r_id):
        query = "DELETE FROM routes WHERE id = ?"
        return self.db.execute_query(query, (r_id,))
