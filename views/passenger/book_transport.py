from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox
from views.common import TablePage
from models.assignment_model import AssignmentModel
from services.assignment_service import AssignmentService
from database.db_handler import DatabaseHandler

class BookTransportPage(TablePage):
    def __init__(self, username):
        self.username = username
        self.db = DatabaseHandler()
        self.service = AssignmentService()
        self.assignment_model = AssignmentModel()
        
        # Get passenger ID
        self.p_id = self.db.execute_scalar("SELECT p.id FROM passengers p JOIN users u ON p.user_id = u.id WHERE u.username = ?", (self.username,))
        
        columns = ['ID', 'Route', 'Departure', 'Arrival', 'Fare (Rs.)']
        rows = self._get_available_trips()
        super().__init__('Book Transport', 'Reserve a seat on an active transport route', columns, rows)

        btn_layout = QHBoxLayout()
        book_btn = QPushButton('Confirm Booking')
        book_btn.clicked.connect(self.process_booking)
        
        btn_layout.addWidget(book_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def _supports_monthly_fare(self):
        return self.db.execute_scalar(
            "SELECT COL_LENGTH('assignments', 'monthly_fare')"
        ) is not None

    def _get_available_trips(self):
        """Get available trips that the passenger hasn't booked yet, showing the actual fare."""
        if self._supports_monthly_fare():
            query = """
                SELECT a.id, 
                       r.origin + ' to ' + r.destination AS route,
                       FORMAT(s.departure_time, 'yyyy-MM-dd HH:mm') AS departure,
                       FORMAT(s.arrival_time, 'yyyy-MM-dd HH:mm') AS arrival,
                       a.monthly_fare AS fare
                FROM assignments a
                JOIN routes r ON a.route_id = r.id
                JOIN schedules s ON s.assignment_id = a.id
                WHERE a.status = 'Active' 
                  AND s.status = 'Scheduled'
                  AND a.id NOT IN (SELECT assignment_id FROM bookings WHERE passenger_id = ? AND status != 'Cancelled')
                ORDER BY s.departure_time
            """
        else:
            query = """
                SELECT a.id, 
                       r.origin + ' to ' + r.destination AS route,
                       FORMAT(s.departure_time, 'yyyy-MM-dd HH:mm') AS departure,
                       FORMAT(s.arrival_time, 'yyyy-MM-dd HH:mm') AS arrival,
                       CAST(500.00 AS DECIMAL(10,2)) AS fare
                FROM assignments a
                JOIN routes r ON a.route_id = r.id
                JOIN schedules s ON s.assignment_id = a.id
                WHERE a.status = 'Active' 
                  AND s.status = 'Scheduled'
                  AND a.id NOT IN (SELECT assignment_id FROM bookings WHERE passenger_id = ? AND status != 'Cancelled')
                ORDER BY s.departure_time
            """
        if self.p_id is None:
            return []
        return self.db.execute_query(query, (self.p_id,), fetch=True)

    def process_booking(self):
        if self.p_id is None:
            QMessageBox.warning(self, 'Profile Missing', 'No passenger profile is linked to this account. Ask an administrator to create your passenger record.')
            return
        row = self.table.currentRow()
        if row < 0: 
            QMessageBox.warning(self, 'No Selection', 'Please select a trip to book.')
            return
        a_id = int(self.table.item(row, 0).text())
        
        try:
            self.service.allocate_passenger(a_id, self.p_id)
            QMessageBox.information(self, 'Booked', 'Seat reserved successfully. The trip details will now appear in your Billing panel.')
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Booking Error', str(e))
    
    def refresh(self):
        self.update_table(self._get_available_trips())
