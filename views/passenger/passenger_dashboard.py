from PyQt5.QtWidgets import QPushButton
from views.common import TablePage
from database.db_handler import DatabaseHandler


class PassengerDashboardPage(TablePage):
    def __init__(self, username):
        self.username = username
        self.db = DatabaseHandler()
        self.p_id = self.db.execute_scalar(
            "SELECT p.id FROM passengers p JOIN users u ON p.user_id = u.id WHERE u.username = ?",
            (username,),
        )

        columns = ['Booking ID', 'Route', 'Date', 'Trip Status', 'Payment Status']
        rows = self._get_bookings()
        super().__init__(
            'Passenger Dashboard',
            'Your confirmed bookings and trip history',
            columns,
            rows,
        )
        self._strip_invoice_pdf_button()

    def _strip_invoice_pdf_button(self):
        """Invoice PDF export belongs on the Billing tab only."""
        for btn in self.findChildren(QPushButton):
            if btn.text() == 'Download Invoice PDF':
                btn.deleteLater()

    def _get_bookings(self):
        """Fetch only bookings for this passenger with their payment status."""
        if self.p_id is None:
            return []
        query = """
            SELECT b.id,
                   r.origin + ' to ' + r.destination,
                   FORMAT(b.booking_date, 'yyyy-MM-dd HH:mm') AS booking_date,
                   b.status AS trip_status,
                   COALESCE(tf.status, 'N/A') AS payment_status
            FROM bookings b
            JOIN assignments a ON b.assignment_id = a.id
            JOIN routes r ON a.route_id = r.id
            LEFT JOIN transport_fees tf
                ON b.passenger_id = tf.passenger_id AND b.assignment_id = tf.assignment_id
            WHERE b.passenger_id = ?
            ORDER BY b.booking_date DESC
        """
        return self.db.execute_query(query, (self.p_id,), fetch=True)

    def refresh(self):
        self.update_table(self._get_bookings())
