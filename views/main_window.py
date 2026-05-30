from inspect import signature

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QListWidget, QListWidgetItem, 
    QStackedWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from views.admin.dashboard import AdminDashboardPage
from views.admin.vehicle_management import VehicleManagementPage
from views.admin.driver_management import DriverManagementPage
from views.admin.assignment_workflow import AssignmentWorkflowPage
from views.admin.route_management import RouteManagementPage
from views.admin.schedule_management import ScheduleManagementPage
from views.admin.fuel_management import FuelManagementPage
from views.admin.tracking_panel import TrackingPanelPage
from views.admin.reports import ReportsPage
from views.driver.driver_dashboard import DriverDashboardPage
from views.driver.report_issue import ReportIssuePage
from views.passenger.passenger_dashboard import PassengerDashboardPage
from views.passenger.book_transport import BookTransportPage
from views.passenger.billing_panel import BillingPanelPage
from views.maintenance.maintenance_dashboard import MaintenanceDashboardPage

# Define Role-Based Navigation without emojis
NAV_CONFIG = {
    'Administrator': [
        ('Dashboard', AdminDashboardPage),
        ('Assignments', AssignmentWorkflowPage),
        ('Routes', RouteManagementPage),
        ('Schedules', ScheduleManagementPage),
        ('Vehicles', VehicleManagementPage),
        ('Drivers', DriverManagementPage),
        ('Fuel', FuelManagementPage),
        ('Tracking', TrackingPanelPage),
        ('Reports', ReportsPage),
    ],
    'Driver': [
        ('Dashboard', DriverDashboardPage),
        ('Report Issue', ReportIssuePage),
    ],
    'Passenger': [
        ('Dashboard', PassengerDashboardPage),
        ('Book Transport', BookTransportPage),
        ('Billing', BillingPanelPage),
    ],
    'Maintenance': [
        ('Dashboard', MaintenanceDashboardPage),
    ],
}

class MainWindow(QMainWindow):
    def __init__(self, user_data: dict):
        super().__init__()
        self.setWindowTitle('Transport Management System')
        self.resize(1200, 800)
        
        self.username = user_data.get('username', 'User')
        self.role = user_data.get('role', 'User')

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar
        sidebar = QFrame()
        sidebar.setObjectName('SidebarFrame')
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)

        brand = QLabel('TMS')
        brand.setObjectName('SidebarTitle')
        brand.setAlignment(Qt.AlignCenter)
        
        user_info = QLabel(f'Signed in as:\n{self.username}')
        user_info.setStyleSheet('color: #636E72; font-size: 9pt; margin-bottom: 20px;')
        user_info.setAlignment(Qt.AlignCenter)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName('NavList')
        self.nav_list.setCursor(Qt.PointingHandCursor)
        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        logout_btn = QPushButton('Sign Out')
        logout_btn.setObjectName('secondaryBtn')
        logout_btn.setFixedHeight(40)
        logout_btn.clicked.connect(self.close)

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(user_info)
        sidebar_layout.addWidget(self.nav_list, 1) # Make nav_list expand to fill space
        sidebar_layout.addWidget(logout_btn)

        # 2. Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        # 3. Assemble
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_container, 1)

        # Load Navigation
        self._setup_navigation()

    def _setup_navigation(self):
        pages = NAV_CONFIG.get(self.role, [])
        for title, page_class in pages:
            self.nav_list.addItem(title)
            sig_params = signature(page_class.__init__).parameters
            if 'username' in sig_params:
                page_instance = page_class(self.username)
            else:
                page_instance = page_class()
            self.stack.addWidget(page_instance)
        
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)
