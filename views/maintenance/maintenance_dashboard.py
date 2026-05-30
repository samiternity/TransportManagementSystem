from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QDateEdit, QInputDialog, QDialog
from PyQt5.QtCore import QDate, Qt
from views.common import TablePage
from models.maintenance_model import MaintenanceModel
from services.maintenance_service import MaintenanceService

class MaintenanceDashboardPage(TablePage):
    def __init__(self):
        self.model = MaintenanceModel()
        self.service = MaintenanceService()
        columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed', 'Driver']
        rows = self.model.get_all()
        # Filter for display (first 7 columns)
        display_rows = [r[:7] for r in rows]
        super().__init__('Maintenance Control', 'Manage repair requests and fleet health', columns, display_rows)

        btn_layout = QHBoxLayout()
        sched_btn = QPushButton('Schedule Repair')
        sched_btn.clicked.connect(self.schedule_repair)
        
        comp_btn = QPushButton('Mark Completed')
        comp_btn.setObjectName('secondaryBtn')
        comp_btn.clicked.connect(self.complete_repair)
        
        btn_layout.addWidget(sched_btn)
        btn_layout.addWidget(comp_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def schedule_repair(self):
        row = self.table.currentRow()
        if row < 0: return
        r_id = int(self.table.item(row, 0).text())
        
        # Simple date picker
        date_dlg = QDialog(self)
        date_dlg.setWindowTitle("Schedule Date")
        vbox = QVBoxLayout(date_dlg)
        date_in = QDateEdit()
        date_in.setCalendarPopup(True)
        date_in.setDate(QDate.currentDate())
        vbox.addWidget(date_in)
        btn = QPushButton("Set Schedule")
        btn.clicked.connect(date_dlg.accept)
        vbox.addWidget(btn)
        
        if date_dlg.exec_():
            date_str = date_in.date().toString('yyyy-MM-dd')
            self.service.schedule_maintenance(r_id, date_str)
            self.refresh()

    def complete_repair(self):
        row = self.table.currentRow()
        if row < 0: return
        r_id = int(self.table.item(row, 0).text())
        
        cost, ok = QInputDialog.getDouble(self, "Completion Cost", "Enter repair cost:", 0, 0, 1000000, 2)
        if ok:
            self.service.resolve_maintenance(r_id, cost)
            self.refresh()

    def refresh(self):
        rows = self.model.get_all()
        display_rows = [r[:7] for r in rows]
        self.update_table(display_rows)
