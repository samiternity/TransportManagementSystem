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
