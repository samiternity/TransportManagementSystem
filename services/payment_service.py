from models.payment_model import PaymentModel

class PaymentService:
    def __init__(self):
        self.model = PaymentModel()

    def automate_fee_generation(self, passenger_id, assignment_id, monthly_amount, month_year, due_date):
        """Automatically generates a monthly fee for a passenger assigned to a service."""
        return self.model.generate_fee(passenger_id, assignment_id, monthly_amount, month_year, due_date)

    def process_payment(self, passenger_id, amount, description, fee_id=None):
        """Records a payment and updates the due balance automatically."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        return self.model.record_payment(passenger_id, amount, description, fee_id)

    def get_passenger_billing_status(self, passenger_id):
        """Returns the current billing status for a passenger."""
        if passenger_id is None:
            return {'payments': [], 'outstanding_fees': []}
        payments = self.model.get_passenger_payments(passenger_id)
        outstanding = self.model.get_outstanding_fees(passenger_id)
        return {
            'payments': payments,
            'outstanding_fees': outstanding
        }

    def get_invoice_details(self, fee_id, passenger_id):
        return self.model.get_fee_invoice_details(fee_id, passenger_id)

    def get_fee_id_for_booking(self, booking_id, passenger_id):
        return self.model.get_fee_id_for_booking(booking_id, passenger_id)
