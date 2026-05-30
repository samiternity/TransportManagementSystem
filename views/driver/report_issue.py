from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QComboBox, QFrame
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler
from services.maintenance_service import MaintenanceService

class ReportIssuePage(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.db = DatabaseHandler()
        self.service = MaintenanceService()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel('Report Vehicle Issue')
        title.setObjectName('PageTitle')
        subtitle = QLabel('Submit maintenance requests for your assigned vehicle')
        subtitle.setObjectName('PageSubtitle')
        
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Form Card
        card = QFrame()
        card.setObjectName('StatCard')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        card_layout.addWidget(QLabel('Select Vehicle'))
        self.vehicle_cb = QComboBox()
        self._load_vehicles()
        card_layout.addWidget(self.vehicle_cb)

        card_layout.addWidget(QLabel('Issue Description'))
        self.desc_in = QTextEdit()
        self.desc_in.setPlaceholderText('Describe the problem in detail...')
        card_layout.addWidget(self.desc_in)

        self.submit_btn = QPushButton('Submit Maintenance Request')
        self.submit_btn.setMinimumHeight(45)
        self.submit_btn.clicked.connect(self.submit_report)
        card_layout.addWidget(self.submit_btn)

        layout.addWidget(card)
        layout.addStretch()

    def _load_vehicles(self):
        # Driver should see vehicles from their profile OR their active assignments
        d_id = self.db.execute_scalar("SELECT d.id FROM drivers d JOIN users u ON d.user_id = u.id WHERE u.username = ?", (self.username,))
        query = """
            SELECT DISTINCT v.id, v.plate_number 
            FROM vehicles v
            LEFT JOIN drivers d ON v.id = d.assigned_vehicle_id
            LEFT JOIN assignments a ON v.id = a.vehicle_id
            WHERE d.id = ? OR (a.driver_id = ? AND a.status = 'Active')
        """
        vehicles = self.db.execute_query(query, (d_id, d_id), fetch=True)
        for v in vehicles:
            self.vehicle_cb.addItem(v[1], v[0])

    def submit_report(self):
        v_id = self.vehicle_cb.currentData()
        desc = self.desc_in.toPlainText().strip()
        
        if not v_id or not desc:
            QMessageBox.warning(self, 'Input Error', 'Please select a vehicle and provide a description.')
            return

        d_id = self.db.execute_scalar("SELECT d.id FROM drivers d JOIN users u ON d.user_id = u.id WHERE u.username = ?", (self.username,))
        
        try:
            self.service.report_driver_issue(v_id, desc, d_id)
            QMessageBox.information(self, 'Reported', 'Issue has been logged and vehicle status updated.')
            self.desc_in.clear()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
