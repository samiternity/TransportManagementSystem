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
