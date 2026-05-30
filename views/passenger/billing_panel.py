from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox, QFileDialog
from views.common import TablePage
from database.db_handler import DatabaseHandler
from services.payment_service import PaymentService
from utils.pdf_documents import build_invoice_pdf

class BillingPanelPage(TablePage):
    def __init__(self, username):
        self.username = username
        self.db = DatabaseHandler()
        self.service = PaymentService()
        
        # Get passenger details
        self.p_id = self.db.execute_scalar("SELECT p.id FROM passengers p JOIN users u ON p.user_id = u.id WHERE u.username = ?", (self.username,))
        if self.p_id is None:
            self.balance = 0.0
        else:
            raw_balance = self.db.execute_scalar(
                "SELECT ISNULL(outstanding_balance, 0) FROM passengers WHERE id = ?", (self.p_id,)
            )
            self.balance = float(raw_balance or 0)
        
        columns = ['ID', 'Trip / Service', 'Amount', 'Billing Period', 'Due Date']
        status = self.service.get_passenger_billing_status(self.p_id)
        rows = status['outstanding_fees']
        
        super().__init__('Billing & Payments', 'Manage your transport dues and clear outstanding balances', columns, rows)

        # Balance Card
        balance_card = QFrame()
        balance_card.setObjectName('StatCard')
        balance_card.setFixedHeight(100)
        bal_layout = QVBoxLayout(balance_card)
        
        bal_title = QLabel('Total Outstanding Balance')
        bal_title.setStyleSheet('color: #636E72; font-size: 10pt;')
        self.bal_val = QLabel(f"${float(self.balance or 0):,.2f}")
        self.bal_val.setStyleSheet('color: #D63031; font-size: 20pt; font-weight: bold;')
        
        bal_layout.addWidget(bal_title)
        bal_layout.addWidget(self.bal_val)
        
        self.layout().insertWidget(1, balance_card)

        # Action Buttons
        btn_layout = QHBoxLayout()
        
        pay_selected_btn = QPushButton('Pay Selected Invoice')
        pay_selected_btn.setObjectName('secondaryBtn')
        pay_selected_btn.clicked.connect(self.pay_selected)

        invoice_pdf_btn = QPushButton('Download Invoice PDF')
        invoice_pdf_btn.setObjectName('secondaryBtn')
        invoice_pdf_btn.setFixedWidth(300)
        invoice_pdf_btn.clicked.connect(self.download_invoice_pdf)
        
        clear_all_btn = QPushButton('Clear All Outstanding Balance')
        clear_all_btn.clicked.connect(self.clear_all_balance)
        
        btn_layout.addWidget(pay_selected_btn)
        btn_layout.addWidget(invoice_pdf_btn)
        btn_layout.addWidget(clear_all_btn)
        btn_layout.addStretch()
        self.layout().addLayout(btn_layout)

    def download_invoice_pdf(self):
        if self.p_id is None:
            QMessageBox.warning(self, 'Profile Missing', 'No passenger profile is linked to this account.')
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an invoice from the table.')
            return

        fee_id = int(self.table.item(row, 0).text())
        invoice = self.service.get_invoice_details(fee_id, self.p_id)
        if not invoice:
            QMessageBox.warning(self, 'Not Found', 'Invoice details could not be loaded.')
            return

        default_name = f"invoice_{invoice['invoice_id']}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Invoice PDF',
            default_name,
            'PDF Files (*.pdf)',
        )
        if not path:
            return
        if not path.lower().endswith('.pdf'):
            path += '.pdf'

        try:
            build_invoice_pdf(path, invoice)
            QMessageBox.information(self, 'Success', f'Invoice saved to:\n{path}')
        except Exception as e:
            QMessageBox.critical(self, 'Export Failed', str(e))

    def pay_selected(self):
        if self.p_id is None:
            QMessageBox.warning(self, 'Profile Missing', 'No passenger profile is linked to this account.')
            return
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an invoice from the table to pay.')
            return
            
        fee_id = int(self.table.item(row, 0).text())
        amount_text = self.table.item(row, 2).text()
        # Handle formatting if any (though usually it's raw from DB)
        amount = float(amount_text.replace('$', '').replace(',', ''))
        
        try:
            self.service.process_payment(self.p_id, amount, f'Individual Payment for Invoice #{fee_id}', fee_id)
            QMessageBox.information(self, 'Payment Success', f'Invoice #{fee_id} has been paid and your balance updated.')
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Payment Error', str(e))

    def clear_all_balance(self):
        if self.p_id is None:
            QMessageBox.warning(self, 'Profile Missing', 'No passenger profile is linked to this account.')
            return
        if self.balance <= 0:
            QMessageBox.information(self, 'Zero Balance', 'You have no outstanding balance to pay at this time.')
            return
            
        if QMessageBox.question(self, 'Confirm Payment', f'Are you sure you want to clear your total balance of ${self.balance:,.2f}?') == QMessageBox.No:
            return

        try:
            # Record a single total payment
            self.service.process_payment(self.p_id, self.balance, 'Lump-sum payment of all outstanding dues')
            # Mark all unpaid fees as Paid
            self.db.execute_query("UPDATE transport_fees SET status = 'Paid' WHERE passenger_id = ? AND status = 'Unpaid'", (self.p_id,))
            QMessageBox.information(self, 'Success', 'Your entire outstanding balance has been cleared successfully.')
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Payment Error', str(e))

    def refresh(self):
        status = self.service.get_passenger_billing_status(self.p_id)
        self.update_table(status['outstanding_fees'])
        if self.p_id is None:
            self.balance = 0.0
        else:
            raw_balance = self.db.execute_scalar(
                "SELECT ISNULL(outstanding_balance, 0) FROM passengers WHERE id = ?", (self.p_id,)
            )
            self.balance = float(raw_balance or 0)
        self.bal_val.setText(f"${float(self.balance or 0):,.2f}")
