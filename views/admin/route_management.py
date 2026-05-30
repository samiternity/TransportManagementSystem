from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QComboBox
from views.common import TablePage, EnterpriseDialog
from models.route_model import RouteModel

class RouteDialog(EnterpriseDialog):
    def __init__(self, parent=None, route=None):
        super().__init__('Route Details', parent)
        self.route = route
        
        self.orig_in = QLineEdit(route[1] if route else "")
        self.dest_in = QLineEdit(route[2] if route else "")
        self.dist_in = QLineEdit(str(route[3]) if route else "")
        self.dur_in = QLineEdit(str(route[4]) if route else "")
        self.status_in = QComboBox()
        self.status_in.addItems(['Active', 'Inactive'])
        if route: self.status_in.setCurrentText(route[5])
        
        self.form_layout.addRow('Origin', self.orig_in)
        self.form_layout.addRow('Destination', self.dest_in)
        self.form_layout.addRow('Distance (km)', self.dist_in)
        self.form_layout.addRow('Duration (min)', self.dur_in)
        self.form_layout.addRow('Status', self.status_in)
        self.add_buttons()

    def get_data(self):
        return (
            self.orig_in.text(), self.dest_in.text(), 
            float(self.dist_in.text() or 0), int(self.dur_in.text() or 0)
        )
    
    def get_full_data(self):
        return self.get_data() + (self.status_in.currentText(),)

class RouteManagementPage(TablePage):
    def __init__(self):
        self.model = RouteModel()
        columns = ['ID', 'Origin', 'Destination', 'Distance', 'Duration', 'Status']
        rows = self.model.get_all()
        super().__init__('Route Management', 'Configure network origins and destinations', columns, rows)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Route')
        add_btn.clicked.connect(self.add_route)
        
        edit_btn = QPushButton('Edit Selection')
        edit_btn.setObjectName('secondaryBtn')
        edit_btn.clicked.connect(self.edit_route)
        
        del_btn = QPushButton('Remove')
        del_btn.setObjectName('dangerBtn')
        del_btn.clicked.connect(self.delete_route)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def add_route(self):
        dlg = RouteDialog(self)
        if dlg.exec_():
            try:
                self.model.create(*dlg.get_data())
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def edit_route(self):
        row_idx = self.table.currentRow()
        if row_idx < 0: return
        r_id = int(self.table.item(row_idx, 0).text())
        rows = self.model.get_all()
        route = next((r for r in rows if r[0] == r_id), None)
        
        dlg = RouteDialog(self, route)
        if dlg.exec_():
            try:
                self.model.update(r_id, *dlg.get_full_data())
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, 'Error', str(e))

    def delete_route(self):
        row_idx = self.table.currentRow()
        if row_idx < 0: return
        r_id = int(self.table.item(row_idx, 0).text())
        if QMessageBox.question(self, 'Confirm', 'Delete this route?') == QMessageBox.Yes:
            self.model.delete(r_id)
            self.refresh()

    def refresh(self):
        self.update_table(self.model.get_all())
