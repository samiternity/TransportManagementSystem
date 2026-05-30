from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QComboBox
from views.common import TablePage, EnterpriseDialog
from database.db_handler import DatabaseHandler

class FuelDialog(EnterpriseDialog):
    def __init__(self, parent=None, vehicles=[]):
        super().__init__('Refill Record', parent)
        self.vehicle_cb = QComboBox()
        for v in vehicles:
            self.vehicle_cb.addItem(v[1], v[0])
            
        self.liters_in = QLineEdit()
        self.cost_in = QLineEdit()
        self.odom_in = QLineEdit()
        
        self.form_layout.addRow('Vehicle', self.vehicle_cb)
        self.form_layout.addRow('Liters', self.liters_in)
        self.form_layout.addRow('Total Cost', self.cost_in)
        self.form_layout.addRow('Odometer Reading', self.odom_in)
        self.add_buttons()

    def get_data(self):
        return (
            self.vehicle_cb.currentData(),
            float(self.liters_in.text() or 0),
            float(self.cost_in.text() or 0),
            int(self.odom_in.text() or 0)
        )

class FuelManagementPage(TablePage):
    def __init__(self):
        self.db = DatabaseHandler()
        columns = ['ID', 'Vehicle', 'Date', 'Liters', 'Cost', 'Odometer']
        rows = self._get_logs()
        super().__init__('Fuel Management', 'Track fuel consumption and refill costs', columns, rows)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Log Refill')
        add_btn.clicked.connect(self.add_log)
        
        edit_btn = QPushButton('Edit Selection')
        edit_btn.setObjectName('secondaryBtn')
        edit_btn.clicked.connect(self.edit_log)
        
        del_btn = QPushButton('Remove')
        del_btn.setObjectName('dangerBtn')
        del_btn.clicked.connect(self.delete_log)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def _get_logs(self):
        return self.db.execute_query(
            "SELECT f.id, v.plate_number, f.log_date, f.liters, f.cost, f.odometer "
            "FROM fuel_logs f JOIN vehicles v ON f.vehicle_id = v.id ORDER BY f.log_date DESC",
            fetch=True
        )

    def add_log(self):
        vehicles = self.db.execute_query("SELECT id, plate_number FROM vehicles", fetch=True)
        dlg = FuelDialog(self, vehicles)
        if dlg.exec_():
            try:
                self.db.execute_query(
                    "INSERT INTO fuel_logs (vehicle_id, liters, cost, odometer) VALUES (?, ?, ?, ?)",
                    dlg.get_data()
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def edit_log(self):
        row_idx = self.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a fuel log to edit.')
            return
        f_id = int(self.table.item(row_idx, 0).text())
        current_liters = self.table.item(row_idx, 3).text()
        current_cost = self.table.item(row_idx, 4).text()
        
        from PyQt5.QtWidgets import QInputDialog
        new_liters, ok1 = QInputDialog.getDouble(self, 'Edit Fuel Log', 'Liters:', float(current_liters), 0, 10000, 2)
        if ok1:
            new_cost, ok2 = QInputDialog.getDouble(self, 'Edit Fuel Log', 'Cost:', float(current_cost), 0, 1000000, 2)
            if ok2:
                try:
                    self.db.execute_query("UPDATE fuel_logs SET liters = ?, cost = ? WHERE id = ?", (new_liters, new_cost, f_id))
                    self.refresh()
                except Exception as e:
                    QMessageBox.critical(self, 'Error', str(e))
    
    def delete_log(self):
        row_idx = self.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a fuel log to remove.')
            return
        f_id = int(self.table.item(row_idx, 0).text())
        if QMessageBox.question(self, 'Confirm', 'Delete this fuel log?') == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM fuel_logs WHERE id = ?", (f_id,))
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Cannot delete: {e}')
    
    def refresh(self):
        self.update_table(self._get_logs())
