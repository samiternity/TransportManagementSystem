from PyQt5.QtWidgets import QMessageBox, QPushButton, QHBoxLayout, QLineEdit, QComboBox
from views.common import TablePage, EnterpriseDialog
from database.db_handler import DatabaseHandler

class TrackingLogDialog(EnterpriseDialog):
    def __init__(self, parent=None, schedules=[]):
        super().__init__('Log Vehicle Coordinates', parent)
        self.schedule_cb = QComboBox()
        for s in schedules:
            self.schedule_cb.addItem(s[1], s[0])
            
        self.lat_in = QLineEdit()
        self.lon_in = QLineEdit()
        self.status_in = QComboBox()
        self.status_in.addItems(['On Track', 'Deviated', 'Stopped'])
        
        self.form_layout.addRow('Active Schedule', self.schedule_cb)
        self.form_layout.addRow('Latitude', self.lat_in)
        self.form_layout.addRow('Longitude', self.lon_in)
        self.form_layout.addRow('Status', self.status_in)
        self.add_buttons()

    def get_data(self):
        return (
            self.schedule_cb.currentData(),
            float(self.lat_in.text() or 0),
            float(self.lon_in.text() or 0),
            self.status_in.currentText()
        )

class TrackingPanelPage(TablePage):
    def __init__(self):
        self.db = DatabaseHandler()
        columns = ['ID', 'Schedule', 'Lat', 'Lon', 'Time', 'Status', 'Alert']
        rows = self.fetch_tracking_data()
        super().__init__('Vehicle Tracking', 'Monitor real-time vehicle coordinates and route adherence', columns, rows)

        btn_layout = QHBoxLayout()
        log_btn = QPushButton('Log New Coordinates')
        log_btn.clicked.connect(self.show_log_dialog)
        
        check_btn = QPushButton('Check Route Deviations')
        check_btn.setObjectName('secondaryBtn')
        check_btn.clicked.connect(self.check_deviations)
        
        edit_btn = QPushButton('Edit Selection')
        edit_btn.setObjectName('secondaryBtn')
        edit_btn.clicked.connect(self.edit_tracking)
        
        del_btn = QPushButton('Remove')
        del_btn.setObjectName('dangerBtn')
        del_btn.clicked.connect(self.delete_tracking)
        
        btn_layout.addWidget(log_btn)
        btn_layout.addWidget(check_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def fetch_tracking_data(self):
        query = """
            SELECT t.id, r.origin + '-' + r.destination, t.latitude, t.longitude, t.timestamp, t.status,
            CASE WHEN t.status = 'Deviated' THEN '⚠️ ROUTE DEVIATION' ELSE 'Normal' END
            FROM tracking_logs t
            JOIN schedules s ON t.schedule_id = s.id
            JOIN assignments a ON s.assignment_id = a.id
            JOIN routes r ON a.route_id = r.id
            ORDER BY t.timestamp DESC
        """
        return self.db.execute_query(query, fetch=True)

    def show_log_dialog(self):
        # Fetch active schedules
        schedules = self.db.execute_query(
            "SELECT s.id, r.origin + ' to ' + r.destination "
            "FROM schedules s JOIN assignments a ON s.assignment_id = a.id "
            "JOIN routes r ON a.route_id = r.id WHERE s.status = 'Scheduled'",
            fetch=True
        )
        if not schedules:
            QMessageBox.warning(self, 'No Active Schedules', 'There are no active schedules to log tracking for.')
            return
            
        dlg = TrackingLogDialog(self, schedules)
        if dlg.exec_():
            try:
                self.db.execute_query(
                    "INSERT INTO tracking_logs (schedule_id, latitude, longitude, timestamp, status) VALUES (?, ?, ?, GETDATE(), ?)",
                    dlg.get_data()
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def check_deviations(self):
        try:
            self.db.execute_query(
                "UPDATE tracking_logs SET status = 'Deviated' WHERE ABS(latitude) > 90 OR ABS(longitude) > 180"
            )
            QMessageBox.information(self, 'Analysis Complete', 'Route deviation check performed.')
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
    def edit_tracking(self):
        row_idx = self.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a tracking record to edit.')
            return
        t_id = int(self.table.item(row_idx, 0).text())
        current_status = self.table.item(row_idx, 5).text()
        
        from PyQt5.QtWidgets import QInputDialog
        statuses = ['On Track', 'Deviated', 'Stopped']
        new_status, ok = QInputDialog.getItem(self, 'Edit Tracking', 'Status:', statuses, statuses.index(current_status) if current_status in statuses else 0, False)
        if ok:
            try:
                self.db.execute_query("UPDATE tracking_logs SET status = ? WHERE id = ?", (new_status, t_id))
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))
    
    def delete_tracking(self):
        row_idx = self.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a tracking record to remove.')
            return
        t_id = int(self.table.item(row_idx, 0).text())
        if QMessageBox.question(self, 'Confirm', 'Delete this tracking log?') == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM tracking_logs WHERE id = ?", (t_id,))
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Cannot delete: {e}')

    def refresh(self):
        self.update_table(self.fetch_tracking_data())
