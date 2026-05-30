from views.common import TablePage
from database.db_handler import DatabaseHandler
from PyQt5.QtWidgets import QMessageBox, QPushButton, QHBoxLayout

class ScheduleManagementPage(TablePage):
    def __init__(self):
        self.db = DatabaseHandler()
        self._auto_complete_schedules()
        
        columns = ['ID', 'Route', 'Driver', 'Vehicle', 'Departure', 'Arrival', 'Status']
        rows = self.fetch_schedules()
        super().__init__('Schedule Management', 'Monitor auto-generated transport schedules', columns, rows)
        
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton('Edit Selection')
        edit_btn.setObjectName('secondaryBtn')
        edit_btn.clicked.connect(self.edit_schedule)
        
        del_btn = QPushButton('Remove')
        del_btn.setObjectName('dangerBtn')
        del_btn.clicked.connect(self.delete_schedule)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def _auto_complete_schedules(self):
        """Automatically marks schedules as 'Completed' if arrival time has passed."""
        try:
            self.db.execute_query(
                "UPDATE schedules SET status = 'Completed' WHERE arrival_time < GETDATE() AND status = 'Scheduled'"
            )
        except Exception as e:
            print(f"Error auto-completing schedules: {e}")

    def fetch_schedules(self):
        query = """
            SELECT s.id, r.origin + ' to ' + r.destination, d.name, v.plate_number, 
                   s.departure_time, s.arrival_time, s.status
            FROM schedules s
            JOIN assignments a ON s.assignment_id = a.id
            JOIN routes r ON a.route_id = r.id
            LEFT JOIN drivers d ON a.driver_id = d.id
            LEFT JOIN vehicles v ON a.vehicle_id = v.id
            ORDER BY s.departure_time DESC
        """
        return self.db.execute_query(query, fetch=True)

    def edit_schedule(self):
        row_idx = self.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a schedule to edit.')
            return
        s_id = int(self.table.item(row_idx, 0).text())
        current_status = self.table.item(row_idx, 6).text()
        
        from PyQt5.QtWidgets import QInputDialog
        statuses = ['Scheduled', 'Completed', 'Cancelled', 'Delayed']
        new_status, ok = QInputDialog.getItem(self, 'Edit Schedule', 'Status:', statuses, statuses.index(current_status) if current_status in statuses else 0, False)
        if ok:
            try:
                self.db.execute_query("UPDATE schedules SET status = ? WHERE id = ?", (new_status, s_id))
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))
    
    def delete_schedule(self):
        row_idx = self.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a schedule to remove.')
            return
        
        s_id = int(self.table.item(row_idx, 0).text())
        if QMessageBox.question(self, 'Confirm', 'Delete this schedule? This will also remove all tracking logs for this schedule.') == QMessageBox.Yes:
            try:
                # 1. Get assignment info before deleting schedule
                assignment_id = self.db.execute_scalar("SELECT assignment_id FROM schedules WHERE id = ?", (s_id,))
                
                # 2. Delete tracking logs and schedule
                self.db.execute_query("DELETE FROM tracking_logs WHERE schedule_id = ?", (s_id,))
                self.db.execute_query("DELETE FROM schedules WHERE id = ?", (s_id,))
                
                # 3. Check if any other schedules remain for this assignment
                remaining = self.db.execute_scalar("SELECT COUNT(*) FROM schedules WHERE assignment_id = ?", (assignment_id,))
                
                if remaining == 0:
                    # 4. Cleanup assignment and revert statuses
                    details = self.db.execute_query(
                        "SELECT vehicle_id, driver_id FROM assignments WHERE id = ?", (assignment_id,), fetch=True
                    )
                    if details:
                        v_id, d_id = details[0]
                        # Revert statuses
                        self.db.execute_query("UPDATE vehicles SET status = 'Available' WHERE id = ?", (v_id,))
                        self.db.execute_query("UPDATE drivers SET status = 'Available', assigned_vehicle_id = NULL WHERE id = ?", (d_id,))
                        
                        # 5. Handle Bookings and Fees (Passenger Financials)
                        # Mark bookings as cancelled
                        self.db.execute_query("UPDATE bookings SET status = 'Cancelled' WHERE assignment_id = ?", (assignment_id,))
                        
                        # Refund passenger balances for unpaid fees on this assignment
                        refund_query = """
                            UPDATE p
                            SET p.outstanding_balance = p.outstanding_balance - f.amount
                            FROM passengers p
                            JOIN transport_fees f ON p.id = f.passenger_id
                            WHERE f.assignment_id = ? AND f.status = 'Unpaid'
                        """
                        self.db.execute_query(refund_query, (assignment_id,))
                        
                        # Void the fees
                        self.db.execute_query("UPDATE transport_fees SET status = 'Cancelled' WHERE assignment_id = ? AND status = 'Unpaid'", (assignment_id,))
                        
                        # Deactivate assignment
                        self.db.execute_query("UPDATE assignments SET status = 'Cancelled' WHERE id = ?", (assignment_id,))
                
                self.refresh()
                QMessageBox.information(self, 'Success', 'Schedule removed and statuses reverted.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Cannot delete: {e}')
    
    def refresh(self):
        self._auto_complete_schedules()
        self.update_table(self.fetch_schedules())
