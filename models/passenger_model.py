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


def add_booking(passenger_name, schedule_id, booking_date, status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT route_id FROM schedules WHERE id = ?', (schedule_id,))
        route_id = cursor.fetchone()[0]
        cursor.execute(
            'INSERT INTO bookings (passenger_name, route_id, schedule_id, booking_date, status) VALUES (?, ?, ?, ?, ?)',
            (passenger_name, route_id, schedule_id, booking_date, status)
        )
        conn.commit()
