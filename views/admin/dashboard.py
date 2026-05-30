from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QStyle
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler

class StatCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setObjectName('StatCard')
        self.setFixedSize(250, 120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet('color: #636E72; font-size: 10pt; font-weight: bold;')
        
        lbl_value = QLabel(str(value))
        lbl_value.setStyleSheet(f'color: {color}; font-size: 20pt; font-weight: bold;')
        
        layout.addWidget(lbl_title)
        layout.addStretch()
        layout.addWidget(lbl_value)

class AdminDashboardPage(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.username = username
        self.db = DatabaseHandler()
        self.stats_layout = QGridLayout()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_container = QVBoxLayout()
        title = QLabel('System Overview')
        title.setObjectName('PageTitle')
        subtitle = QLabel('Real-time statistics and operational status')
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
        
        layout.addWidget(header)

        # Stats Grid
        self.stats_layout.setSpacing(20)
        layout.addLayout(self.stats_layout)
        
        self.refresh()
        layout.addStretch()

    def refresh(self):
        # Clear existing stats
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Fetch Real Data
        v_count = self.db.execute_scalar("SELECT COUNT(*) FROM vehicles")
        d_count = self.db.execute_scalar("SELECT COUNT(*) FROM drivers")
        r_count = self.db.execute_scalar("SELECT COUNT(*) FROM routes")
        m_count = self.db.execute_scalar("SELECT COUNT(*) FROM maintenance_records WHERE status != 'Completed'")
        c_count = self.db.execute_scalar("SELECT COUNT(*) FROM assignments WHERE status = 'Cancelled'")
        rev = self.db.execute_scalar("SELECT ISNULL(SUM(amount), 0) FROM payments")

        self.stats_layout.addWidget(StatCard('Vehicles', v_count, '#0984E3'), 0, 0)
        self.stats_layout.addWidget(StatCard('Drivers', d_count, '#00B894'), 0, 1)
        self.stats_layout.addWidget(StatCard('Routes', r_count, '#6C5CE7'), 0, 2)
        self.stats_layout.addWidget(StatCard('Pending Maintenance', m_count, '#D63031'), 0, 3)
        self.stats_layout.addWidget(StatCard('Total Revenue', f'${rev:,.0f}', '#2D3436'), 1, 0)
        self.stats_layout.addWidget(StatCard('Cancelled Assignments', c_count, '#636E72'), 1, 1)
