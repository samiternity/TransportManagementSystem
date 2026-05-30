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
