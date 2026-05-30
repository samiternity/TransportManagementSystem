from models.passenger_model import get_bookings_for_passenger, add_booking


def list_bookings_for_passenger(name):
    return get_bookings_for_passenger(name)


def add_booking_controller(passenger_name, schedule_id, booking_date, status):
    add_booking(passenger_name, schedule_id, booking_date, status)
