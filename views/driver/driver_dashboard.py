from views.common import TablePage
from database.db_handler import DatabaseHandler

class DriverDashboardPage(TablePage):
    def __init__(self, username):
        self.username = username
        self.db = DatabaseHandler()
        columns = ['ID', 'Driver Name', 'Route', 'Departure', 'Arrival', 'Status']
        rows = self.fetch_driver_schedules()
        super().__init__('Driver Dashboard', f'Assigned schedules for {username}', columns, rows)

    def fetch_driver_schedules(self):
        query = """
            SELECT s.id, d.name, r.origin + ' to ' + r.destination, s.departure_time, s.arrival_time, s.status
            FROM schedules s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN drivers d ON a.driver_id = d.id
            JOIN users u ON d.user_id = u.id
            JOIN routes r ON a.route_id = r.id
            WHERE u.username = ?
            ORDER BY s.departure_time DESC
        """
        return self.db.execute_query(query, (self.username,), fetch=True)

    def refresh(self):
        self.update_table(self.fetch_driver_schedules())
