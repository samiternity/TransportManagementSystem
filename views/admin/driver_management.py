from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QComboBox
from views.common import TablePage, EnterpriseDialog
from database.db_handler import DatabaseHandler
from utils.hashing import hash_password

class DriverDialog(EnterpriseDialog):
    def __init__(self, parent=None, driver=None):
        super().__init__('Driver Details', parent)
        self.driver = driver
        self.is_new = driver is None
        
        self.name_in = QLineEdit(driver[1] if driver else "")
        self.lic_in = QLineEdit(driver[2] if driver else "")
        self.phone_in = QLineEdit(driver[3] if driver else "")
        self.status_in = QComboBox()
        self.status_in.addItems(['Available', 'On Trip', 'On Leave', 'Inactive'])
        if driver: self.status_in.setCurrentText(driver[4])
        
        # Add username/password fields for new drivers only
        if self.is_new:
            self.username_in = QLineEdit()
            self.password_in = QLineEdit()
            self.password_in.setEchoMode(QLineEdit.Password)
            self.form_layout.addRow('Username', self.username_in)
            self.form_layout.addRow('Password', self.password_in)
        
        self.form_layout.addRow('Full Name', self.name_in)
        self.form_layout.addRow('License Number', self.lic_in)
        self.form_layout.addRow('Phone Number', self.phone_in)
        self.form_layout.addRow('Status', self.status_in)
        self.add_buttons()

    def get_data(self):
        data = (
            self.name_in.text(), self.lic_in.text(), self.phone_in.text(),
            self.status_in.currentText(), None # Vehicle ID handled by assignment
        )
        if self.is_new:
            return {
                'driver_data': data,
                'username': self.username_in.text().strip(),
                'password': self.password_in.text()
            }
        return data

class DriverManagementPage(TablePage):
    def __init__(self):
        self.db = DatabaseHandler()
        columns = ['ID', 'Name', 'License', 'Phone', 'Status', 'Username']
        rows = self._get_drivers_with_credentials()
        super().__init__('Driver Management', 'Manage driver records and login credentials', columns, rows)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Driver')
        add_btn.clicked.connect(self.add_driver)
        
        edit_btn = QPushButton('Edit Selection')
        edit_btn.setObjectName('secondaryBtn')
        edit_btn.clicked.connect(self.edit_driver)
        
        del_btn = QPushButton('Remove')
        del_btn.setObjectName('dangerBtn')
        del_btn.clicked.connect(self.delete_driver)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def _get_drivers_with_credentials(self):
        """Fetch drivers with their username for login."""
        query = """
            SELECT d.id, d.name, d.license_number, d.phone, d.status, 
                   COALESCE(u.username, 'N/A')
            FROM drivers d
            LEFT JOIN users u ON d.user_id = u.id
            ORDER BY d.id
        """
        return self.db.execute_query(query, fetch=True)

    def add_driver(self):
        dlg = DriverDialog(self)
        if dlg.exec_():
            try:
                data = dlg.get_data()
                
                # 1. Create user account
                username = data['username']
                password = data['password']
                if not username or not password:
                    QMessageBox.warning(self, 'Missing Fields', 'Username and password are required.')
                    return
                
                pass_hash = hash_password(password)
                self.db.execute_query(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, pass_hash, 'Driver')
                )
                
                # 2. Get the created user_id
                user_id = self.db.execute_scalar("SELECT id FROM users WHERE username = ?", (username,))
                
                # 3. Create driver record with linked user_id
                driver_data = data['driver_data']
                query = "INSERT INTO drivers (user_id, name, license_number, phone, status, assigned_vehicle_id) VALUES (?, ?, ?, ?, ?, ?)"
                self.db.execute_query(query, (user_id, driver_data[0], driver_data[1], driver_data[2], driver_data[3], driver_data[4]))
                
                QMessageBox.information(self, 'Success', f'Driver account created!\nUsername: {username}\nPassword: {password}')
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def edit_driver(self):
        row_idx = self.table.currentRow()
        if row_idx < 0: return
        d_id = int(self.table.item(row_idx, 0).text())
        # Get driver data without username for editing
        rows = self.db.execute_query(
            "SELECT id, name, license_number, phone, status, assigned_vehicle_id FROM drivers WHERE id = ?",
            (d_id,), fetch=True
        )
        driver = rows[0] if rows else None
        
        dlg = DriverDialog(self, driver)
        if dlg.exec_():
            try:
                self.db.execute_query(
                    "UPDATE drivers SET name=?, license_number=?, phone=?, status=?, assigned_vehicle_id=? WHERE id=?",
                    (*dlg.get_data(), d_id)
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def delete_driver(self):
        row_idx = self.table.currentRow()
        if row_idx < 0: return
        d_id = int(self.table.item(row_idx, 0).text())
        if QMessageBox.question(self, 'Confirm', 
            'Delete this driver and ALL their history (assignments, schedules, tracking logs)?\n\n'
            'This cannot be undone. Consider setting status to "Inactive" instead.') == QMessageBox.Yes:
            try:
                # Get all assignments for this driver
                assignments = self.db.execute_query(
                    "SELECT id FROM assignments WHERE driver_id = ?", (d_id,), fetch=True
                )
                # Cascade delete: tracking_logs -> schedules -> assignments -> driver
                for (a_id,) in assignments:
                    # Get schedules for this assignment
                    schedules = self.db.execute_query(
                        "SELECT id FROM schedules WHERE assignment_id = ?", (a_id,), fetch=True
                    )
                    for (s_id,) in schedules:
                        # Delete tracking logs for this schedule
                        self.db.execute_query("DELETE FROM tracking_logs WHERE schedule_id = ?", (s_id,))
                    # Delete schedules for this assignment
                    self.db.execute_query("DELETE FROM schedules WHERE assignment_id = ?", (a_id,))
                # Delete all assignments for this driver
                self.db.execute_query("DELETE FROM assignments WHERE driver_id = ?", (d_id,))
                # Delete the driver record (and their user account)
                driver = self.db.execute_query("SELECT user_id FROM drivers WHERE id = ?", (d_id,), fetch=True)
                self.db.execute_query("DELETE FROM drivers WHERE id = ?", (d_id,))
                if driver and driver[0][0]:
                    self.db.execute_query("DELETE FROM users WHERE id = ?", (driver[0][0],))
                self.refresh()
                QMessageBox.information(self, 'Success', 'Driver and all related records deleted.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Cannot delete driver: {e}')

    def refresh(self):
        rows = self._get_drivers_with_credentials()
        self.update_table(rows)
