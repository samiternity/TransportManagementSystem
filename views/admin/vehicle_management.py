from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QComboBox
from views.common import TablePage, EnterpriseDialog
from models.vehicle_model import VehicleModel

class VehicleDialog(EnterpriseDialog):
    def __init__(self, parent=None, vehicle=None):
        super().__init__('Vehicle Details', parent)
        self.vehicle = vehicle
        
        self.plate_in = QLineEdit(vehicle[1] if vehicle else "")
        self.make_in = QLineEdit(vehicle[2] if vehicle else "")
        self.model_in = QLineEdit(vehicle[3] if vehicle else "")
        self.year_in = QLineEdit(str(vehicle[4]) if vehicle else "")
        self.cap_in = QLineEdit(str(vehicle[5]) if vehicle else "4")
        self.status_in = QComboBox()
        self.status_in.addItems(['Available', 'In Service', 'Maintenance', 'Inactive'])
        if vehicle: self.status_in.setCurrentText(vehicle[6])
        
        self.form_layout.addRow('Plate Number', self.plate_in)
        self.form_layout.addRow('Make', self.make_in)
        self.form_layout.addRow('Model', self.model_in)
        self.form_layout.addRow('Year', self.year_in)
        self.form_layout.addRow('Capacity', self.cap_in)
        self.form_layout.addRow('Status', self.status_in)
        self.add_buttons()

    def get_data(self):
        return (
            self.plate_in.text(), self.make_in.text(), self.model_in.text(),
            int(self.year_in.text() or 0), int(self.cap_in.text() or 4),
            self.status_in.currentText(), 0, 'Petrol' # Defaults
        )

class VehicleManagementPage(TablePage):
    def __init__(self):
        self.model = VehicleModel()
        columns = ['ID', 'Plate', 'Make', 'Model', 'Year', 'Capacity', 'Status']
        rows = self.model.get_all()
        # Filter rows to match columns
        display_rows = [r[:7] for r in rows]
        super().__init__('Vehicle Management', 'Manage fleet assets and availability', columns, display_rows)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Vehicle')
        add_btn.clicked.connect(self.add_vehicle)
        
        edit_btn = QPushButton('Edit Selection')
        edit_btn.setObjectName('secondaryBtn')
        edit_btn.clicked.connect(self.edit_vehicle)
        
        del_btn = QPushButton('Remove')
        del_btn.setObjectName('dangerBtn')
        del_btn.clicked.connect(self.delete_vehicle)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def add_vehicle(self):
        dlg = VehicleDialog(self)
        if dlg.exec_():
            self.model.create(*dlg.get_data())
            self.refresh()

    def edit_vehicle(self):
        row_idx = self.table.currentRow()
        if row_idx < 0: return
        v_id = int(self.table.item(row_idx, 0).text())
        vehicle = self.model.get_by_id(v_id)
        dlg = VehicleDialog(self, vehicle)
        if dlg.exec_():
            self.model.update(v_id, *dlg.get_data())
            self.refresh()

    def delete_vehicle(self):
        row_idx = self.table.currentRow()
        if row_idx < 0: return
        v_id = int(self.table.item(row_idx, 0).text())
        if QMessageBox.question(self, 'Confirm', 'Delete this vehicle? (This will fail if it has history)') == QMessageBox.Yes:
            try:
                self.model.delete(v_id)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(
                    self, 'Dependency Error', 
                    'This vehicle cannot be deleted because it is linked to existing assignments, fuel logs, or maintenance records.\n\n'
                    'Recommended Action: Use "Edit Selection" to set the status to "Inactive" instead.'
                )

    def refresh(self):
        rows = self.model.get_all()
        display_rows = [r[:7] for r in rows]
        self.update_table(display_rows)
