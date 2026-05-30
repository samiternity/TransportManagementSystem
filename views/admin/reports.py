from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QComboBox,
    QPushButton, QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt
from database.db_handler import DatabaseHandler


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        header = QVBoxLayout()
        title = QLabel('System Reports')
        title.setObjectName('PageTitle')
        subtitle = QLabel('Comprehensive metrics and operational analytics')
        subtitle.setObjectName('PageSubtitle')
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Filter by Vehicle:'))
        self.vehicle_cb = QComboBox()
        self.vehicle_cb.addItem('All Vehicles', None)
        self._load_vehicles()
        self.vehicle_cb.currentIndexChanged.connect(self.update_metrics)
        filter_layout.addWidget(self.vehicle_cb)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.metrics_container = QVBoxLayout()
        layout.addLayout(self.metrics_container)

        self.update_metrics()
        layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()
        self.export_pdf_btn = QPushButton('Download PDF Report')
        self.export_pdf_btn.setObjectName('secondaryBtn')
        self.export_pdf_btn.setFixedWidth(270)
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        footer.addWidget(self.export_pdf_btn)
        layout.addLayout(footer)

    def _load_vehicles(self):
        vehicles = self.db.execute_query("SELECT id, plate_number FROM vehicles", fetch=True)
        for v_id, plate in vehicles:
            self.vehicle_cb.addItem(plate, v_id)

    def _metric_queries(self, v_id):
        where_clause = f" WHERE a.vehicle_id = {v_id}" if v_id else ""
        where_clause_fuel = f" WHERE vehicle_id = {v_id}" if v_id else ""
        where_clause_maint = f" WHERE vehicle_id = {v_id}" if v_id else ""
        return [
            ('Total Distance Covered', f"SELECT ISNULL(SUM(distance_km), 0) FROM routes r JOIN assignments a ON r.id = a.route_id{where_clause}", "km"),
            ('Average Fuel Efficiency', f"SELECT ISNULL(AVG(odometer / NULLIF(liters, 0)), 0) FROM fuel_logs{where_clause_fuel}", "km/L"),
            ('Maintenance Completion Rate', f"SELECT CAST(COUNT(CASE WHEN status='Completed' THEN 1 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 FROM maintenance_records{where_clause_maint}", "%"),
            ('Active Driver Utilization', "SELECT CAST(COUNT(CASE WHEN status='On Trip' THEN 1 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 FROM drivers", "%"),
        ]

    def _collect_metrics(self):
        v_id = self.vehicle_cb.currentData()
        rows = []
        for label, query, unit in self._metric_queries(v_id):
            val = self.db.execute_scalar(query)
            if val is None:
                val = 0
            rows.append((label, val, unit))
        return rows

    def update_metrics(self):
        while self.metrics_container.count():
            item = self.metrics_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, val, unit in self._collect_metrics():
            card = QFrame()
            card.setObjectName('StatCard')
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(25, 20, 25, 20)

            lbl_name = QLabel(label)
            lbl_name.setStyleSheet('font-size: 11pt; color: #636E72;')

            lbl_val = QLabel(f"{val:,.1f} {unit}")
            lbl_val.setStyleSheet('font-size: 16pt; font-weight: bold; color: #0984E3;')
            lbl_val.setAlignment(Qt.AlignRight)

            card_layout.addWidget(lbl_name)
            card_layout.addStretch()
            card_layout.addWidget(lbl_val)
            self.metrics_container.addWidget(card)

    def export_pdf(self):
        from utils.pdf_documents import build_operational_report_pdf

        filter_label = self.vehicle_cb.currentText()
        metrics = self._collect_metrics()

        default_name = (
            'transport_report_all_vehicles.pdf'
            if self.vehicle_cb.currentData() is None
            else f"transport_report_{filter_label.replace(' ', '_')}.pdf"
        )

        path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Report PDF',
            default_name,
            'PDF Files (*.pdf)',
        )
        if not path:
            return
        if not path.lower().endswith('.pdf'):
            path += '.pdf'

        try:
            build_operational_report_pdf(path, filter_label, metrics)
            QMessageBox.information(self, 'Success', f'Report saved to:\n{path}')
        except Exception as e:
            QMessageBox.critical(self, 'Export Failed', str(e))
