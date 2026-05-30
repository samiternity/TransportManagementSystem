from database.db_handler import DatabaseHandler

class MaintenanceModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def get_all(self):
        query = """
            SELECT m.id, v.plate_number, m.issue_description, m.status, m.scheduled_date, m.completed_date, d.name
            FROM maintenance_records m
            LEFT JOIN vehicles v ON m.vehicle_id = v.id
            LEFT JOIN drivers d ON m.reported_by_driver_id = d.id
            ORDER BY m.id DESC
        """
        return self.db.execute_query(query, fetch=True)

    def report_issue(self, vehicle_id, description, driver_id=None):
        query = """
            INSERT INTO maintenance_records (vehicle_id, issue_description, reported_by_driver_id, status)
            VALUES (?, ?, ?, 'Reported')
        """
        queries = [
            (query, (vehicle_id, description, driver_id)),
            ("UPDATE vehicles SET status = 'Needs Maintenance' WHERE id = ?", (vehicle_id,))
        ]
        return self.db.execute_transaction(queries)

    def schedule_repair(self, record_id, scheduled_date):
        query = "UPDATE maintenance_records SET status = 'Scheduled', scheduled_date = ? WHERE id = ?"
        return self.db.execute_query(query, (scheduled_date, record_id))

    def complete_repair(self, record_id, cost):
        # Transaction to complete repair and set vehicle back to available
        v_id = self.db.execute_scalar("SELECT vehicle_id FROM maintenance_records WHERE id = ?", (record_id,))
        queries = [
            ("UPDATE maintenance_records SET status = 'Completed', completed_date = GETDATE(), cost = ? WHERE id = ?", (cost, record_id)),
            ("UPDATE vehicles SET status = 'Available' WHERE id = ?", (v_id,))
        ]
        return self.db.execute_transaction(queries)
