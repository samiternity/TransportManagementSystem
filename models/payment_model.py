from database.db_handler import DatabaseHandler

class PaymentModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def get_passenger_payments(self, passenger_id):
        query = "SELECT id, amount, payment_date, description FROM payments WHERE passenger_id = ? ORDER BY payment_date DESC"
        return self.db.execute_query(query, (passenger_id,), fetch=True)

    def get_all_payments(self):
        query = """
            SELECT p.id, ps.name, p.amount, p.payment_date, p.description 
            FROM payments p
            JOIN passengers ps ON p.passenger_id = ps.id
            ORDER BY p.payment_date DESC
        """
        return self.db.execute_query(query, fetch=True)

    def generate_fee(self, passenger_id, assignment_id, amount, month_year, due_date):
        query = """
            INSERT INTO transport_fees (passenger_id, assignment_id, amount, month_year, due_date, status)
            VALUES (?, ?, ?, ?, ?, 'Unpaid')
        """
        # Transaction to generate fee and increase outstanding balance
        queries = [
            (query, (passenger_id, assignment_id, amount, month_year, due_date)),
            ("UPDATE passengers SET outstanding_balance = outstanding_balance + ? WHERE id = ?", (amount, passenger_id))
        ]
        return self.db.execute_transaction(queries)

    def record_payment(self, passenger_id, amount, description, fee_id=None):
        query = """
            INSERT INTO payments (passenger_id, fee_id, amount, payment_date, description)
            VALUES (?, ?, ?, GETDATE(), ?)
        """
        # Transaction to record payment and decrease outstanding balance
        queries = [
            (query, (passenger_id, fee_id, amount, description)),
            ("UPDATE passengers SET outstanding_balance = outstanding_balance - ? WHERE id = ?", (amount, passenger_id))
        ]
        if fee_id:
            queries.append(("UPDATE transport_fees SET status = 'Paid' WHERE id = ?", (fee_id,)))
            
        return self.db.execute_transaction(queries)

    def get_outstanding_fees(self, passenger_id):
        query = """
            SELECT f.id, r.origin + ' to ' + r.destination AS route, f.amount, f.month_year, f.due_date
            FROM transport_fees f
            JOIN assignments a ON f.assignment_id = a.id
            JOIN routes r ON a.route_id = r.id
            WHERE f.passenger_id = ? AND f.status = 'Unpaid'
        """
        return self.db.execute_query(query, (passenger_id,), fetch=True)

    def get_fee_invoice_details(self, fee_id, passenger_id):
        query = """
            SELECT f.id, f.amount, f.month_year, f.due_date, f.status,
                   r.origin + ' to ' + r.destination AS route,
                   p.name, p.phone, u.username
            FROM transport_fees f
            JOIN assignments a ON f.assignment_id = a.id
            JOIN routes r ON a.route_id = r.id
            JOIN passengers p ON f.passenger_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE f.id = ? AND f.passenger_id = ?
        """
        rows = self.db.execute_query(query, (fee_id, passenger_id), fetch=True)
        if not rows:
            return None
        row = rows[0]
        return {
            'invoice_id': row[0],
            'amount': float(row[1]),
            'billing_period': row[2],
            'due_date': row[3],
            'status': row[4],
            'route': row[5],
            'passenger_name': row[6],
            'phone': row[7] or '',
            'username': row[8],
        }

    def get_fee_id_for_booking(self, booking_id, passenger_id):
        query = """
            SELECT TOP 1 f.id
            FROM transport_fees f
            INNER JOIN bookings b
                ON b.assignment_id = f.assignment_id AND b.passenger_id = f.passenger_id
            WHERE b.id = ? AND b.passenger_id = ?
            ORDER BY f.id DESC
        """
        return self.db.execute_scalar(query, (booking_id, passenger_id))
