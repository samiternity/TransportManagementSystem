from views.common import TablePage
from controllers.payment_controller import payments_for_passenger


class PaymentHistoryPage(TablePage):
    def __init__(self, username):
        self.username = username
        columns = ['ID', 'Amount', 'Date', 'Description']
        rows = payments_for_passenger(username)
        super().__init__('Payment History', 'View your transaction history and receipts.', columns, rows)
    
    def refresh(self):
        self.update_table(payments_for_passenger(self.username))
