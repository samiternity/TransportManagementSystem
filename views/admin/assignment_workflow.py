from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QDateEdit, QFrame, QTimeEdit, QLineEdit, QStyle
from PyQt5.QtCore import QDate, Qt, QTime
from views.common import TablePage, EnterpriseDialog
from models.route_model import RouteModel
from models.vehicle_model import VehicleModel
from models.driver_model import DriverModel
from services.assignment_service import AssignmentService
from database.db_handler import DatabaseHandler

class AssignmentWorkflowPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = AssignmentService()
        self.route_model = RouteModel()
        self.vehicle_model = VehicleModel()
        self.driver_model = DriverModel()
        self.db = DatabaseHandler()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)

        # Header
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_container = QVBoxLayout()
        title = QLabel('Transport Assignment Workflow')
        title.setObjectName('PageTitle')
        subtitle = QLabel('Strictly link Routes, Vehicles, and Drivers to generate schedules')
        subtitle.setObjectName('PageSubtitle')
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        refresh_btn = QPushButton(' Refresh')
        refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_btn.setObjectName('secondaryBtn')
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_container)

        # Workflow Form
        form_card = QFrame()
        form_card.setObjectName('StatCard')
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        # Step 1: Select Route
        form_layout.addWidget(QLabel('Step 1: Select Active Route'))
        self.route_cb = QComboBox()
        self._load_routes()
        self.route_cb.currentIndexChanged.connect(self.update_arrival_estimate)
        form_layout.addWidget(self.route_cb)

        # Step 2: Select Available Vehicle
        form_layout.addWidget(QLabel('Step 2: Assign Available Vehicle'))
        self.vehicle_cb = QComboBox()
        self._load_vehicles()
        form_layout.addWidget(self.vehicle_cb)

        # Step 3: Select Available Driver
        form_layout.addWidget(QLabel('Step 3: Assign Available Driver'))
        self.driver_cb = QComboBox()
        self._load_drivers()
        form_layout.addWidget(self.driver_cb)

        # Step 4: Fare & Timing
        extra_layout = QHBoxLayout()
        
        fare_v = QVBoxLayout()
        fare_v.addWidget(QLabel('Monthly Trip Fare ($)'))
        self.fare_in = QLineEdit('500.00')
        fare_v.addWidget(self.fare_in)
        
        date_v = QVBoxLayout()
        date_v.addWidget(QLabel('Commencement Date'))
        self.date_in = QDateEdit()
        self.date_in.setDate(QDate.currentDate())
        self.date_in.setCalendarPopup(True)
        date_v.addWidget(self.date_in)
        
        dep_v = QVBoxLayout()
        dep_v.addWidget(QLabel('Departure Time'))
        self.dep_time = QTimeEdit()
        self.dep_time.setTime(QTime(8, 0))
        self.dep_time.timeChanged.connect(self.update_arrival_estimate)
        dep_v.addWidget(self.dep_time)
        
        arr_v = QVBoxLayout()
        arr_v.addWidget(QLabel('Est. Arrival Time'))
        self.arr_time = QTimeEdit()
        self.arr_time.setTime(QTime(10, 0))
        self.arr_time.setEnabled(True) 
        arr_v.addWidget(self.arr_time)
        
        extra_layout.addLayout(fare_v)
        extra_layout.addLayout(date_v)
        extra_layout.addLayout(dep_v)
        extra_layout.addLayout(arr_v)
        form_layout.addLayout(extra_layout)

        # Action
        self.assign_btn = QPushButton('Generate Transport Assignment')
        self.assign_btn.setMinimumHeight(50)
        self.assign_btn.clicked.connect(self.process_assignment)
        form_layout.addWidget(self.assign_btn)

        layout.addWidget(form_card)
        layout.addStretch()

    def update_arrival_estimate(self):
        r_id = self.route_cb.currentData()
        if not r_id: return
        
        duration = self.db.execute_scalar("SELECT duration_minutes FROM routes WHERE id = ?", (r_id,))
        if duration:
            dep = self.dep_time.time()
            arr = dep.addSecs(duration * 60)
            self.arr_time.setTime(arr)

    def _load_routes(self):
        routes = self.route_model.get_active()
        for r in routes:
            self.route_cb.addItem(f"{r[1]} to {r[2]}", r[0])

    def _load_vehicles(self):
        vehicles = self.vehicle_model.get_available()
        for v in vehicles:
            self.vehicle_cb.addItem(f"{v[1]} ({v[2]} {v[3]}) - Cap: {v[4]}", v[0])

    def _load_drivers(self):
        drivers = self.driver_model.get_available()
        for d in drivers:
            self.driver_cb.addItem(f"{d[1]} (Lic: {d[2]})", d[0])

    def process_assignment(self):
        r_id = self.route_cb.currentData()
        v_id = self.vehicle_cb.currentData()
        d_id = self.driver_cb.currentData()
        date_str = self.date_in.date().toString('yyyy-MM-dd')
        dep_str = self.dep_time.time().toString('HH:mm')
        arr_str = self.arr_time.time().toString('HH:mm')
        fare = float(self.fare_in.text() or 500.0)

        if not all([r_id, v_id, d_id]):
            QMessageBox.warning(self, 'Incomplete', 'Please select all workflow components.')
            return

        try:
            self.service.create_linked_assignment(v_id, d_id, r_id, date_str, dep_str, arr_str, fare)
            QMessageBox.information(self, 'Success', 'Assignment created and single schedule generated.')
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Workflow Error', str(e))

    def refresh(self):
        """Reloads all dropdown lists with the latest available data."""
        self.route_cb.clear()
        self.vehicle_cb.clear()
        self.driver_cb.clear()
        self._load_routes()
        self._load_vehicles()
        self._load_drivers()
