from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QDialog, QLineEdit, 
    QPushButton, QFrame, QFormLayout, QStyle
)
from PyQt5.QtCore import Qt

class TablePage(QWidget):
    """Base class for listing pages with a professional table view."""
    def __init__(self, title, subtitle, columns, rows):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header Section
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_container = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setObjectName('PageTitle')
        lbl_subtitle = QLabel(subtitle)
        lbl_subtitle.setObjectName('PageSubtitle')
        title_container.addWidget(lbl_title)
        title_container.addWidget(lbl_subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton(' Refresh')
        self.refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_btn.setObjectName('secondaryBtn')
        self.refresh_btn.setFixedWidth(140)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(header_container)

        # Table Section
        self.table = QTableWidget()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        
        self.update_table(rows)
        layout.addWidget(self.table)

    def refresh(self):
        """Default refresh behavior. Subclasses should override this."""
        pass

    def update_table(self, rows):
        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(r_idx, c_idx, item)

class EnterpriseDialog(QDialog):
    """Base class for forms with consistent light-theme styling."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(500)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet('font-size: 16pt; font-weight: bold; color: #0984E3;')
        self.layout.addWidget(title_lbl)
        
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setLabelAlignment(Qt.AlignLeft)
        self.layout.addLayout(self.form_layout)

    def add_buttons(self):
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton('Confirm')
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setObjectName('secondaryBtn')
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        self.layout.addLayout(btn_layout)
