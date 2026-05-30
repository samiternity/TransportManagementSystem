from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox, QLabel
from views.common import TablePage
from database.db_handler import DatabaseHandler
from services.payment_service import PaymentService

class BillingManagementPage(TablePage):
    def __init__(self):
        self.db = DatabaseHandler()
        self.service = PaymentService()
        
        columns = ['ID', 'Student', 'Amount', 'Period', 'Due Date', 'Status']
        rows = self.fetch_invoices()
        
        super().__init__('Billing Management', 'Manage student invoices and payment status', columns, rows)

        # Action Buttons
        btn_layout = QHBoxLayout()
        
        paid_btn = QPushButton('Mark as Paid')
        paid_btn.clicked.connect(lambda: self.toggle_status('Paid'))
        
        unpaid_btn = QPushButton('Mark as Unpaid')
        unpaid_btn.clicked.connect(lambda: self.toggle_status('Unpaid'))
        
        btn_layout.addWidget(paid_btn)
        btn_layout.addWidget(unpaid_btn)
        btn_layout.addStretch()
        
        self.layout().addLayout(btn_layout)

    def fetch_invoices(self):
        query = """
            SELECT f.id, p.name, f.amount, f.month_year, f.due_date, f.status
            FROM transport_fees f
            JOIN passengers p ON f.passenger_id = p.id
            ORDER BY f.due_date DESC
        """
        return self.db.execute_query(query, fetch=True)

    def toggle_status(self, new_status):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an invoice to update.')
            return
            
        fee_id = int(self.table.item(row, 0).text())
        current_status = self.table.item(row, 5).text()
        
        if current_status == new_status:
            return

        try:
            # If marking as paid, we should also record a simulated payment
            if new_status == 'Paid':
                p_id = self.db.execute_scalar("SELECT passenger_id FROM transport_fees WHERE id = ?", (fee_id,))
                amount = float(self.table.item(row, 2).text())
                self.service.process_payment(p_id, amount, f'Manual mark as Paid for Fee ID {fee_id}', fee_id)
            else:
                # If marking as unpaid, we revert the status and adjust balance
                # Note: For simplicity, we just update the status here. 
                # In a real app, you'd want to handle the payment reversal.
                p_id = self.db.execute_scalar("SELECT passenger_id FROM transport_fees WHERE id = ?", (fee_id,))
                amount = float(self.table.item(row, 2).text())
                queries = [
                    ("UPDATE transport_fees SET status = 'Unpaid' WHERE id = ?", (fee_id,)),
                    ("UPDATE passengers SET outstanding_balance = outstanding_balance + ? WHERE id = ?", (amount, p_id))
                ]
                self.db.execute_transaction(queries)

            QMessageBox.information(self, 'Success', f'Invoice {fee_id} marked as {new_status}.')
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def refresh_data(self):
        self.update_table(self.fetch_invoices())
