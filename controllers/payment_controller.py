from models.payment_model import PaymentModel
from database.db_handler import DatabaseHandler


def list_payments():
    model = PaymentModel()
    return model.get_all_payments()


def payments_for_passenger(username):
    """Get payments for a passenger by username."""
    db = DatabaseHandler()
    # Get passenger_id from username
    p_id = db.execute_scalar(
        "SELECT p.id FROM passengers p JOIN users u ON p.user_id = u.id WHERE u.username = ?",
        (username,)
    )
    if not p_id:
        return []
    model = PaymentModel()
    return model.get_passenger_payments(p_id)
