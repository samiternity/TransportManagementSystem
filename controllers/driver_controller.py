from models.driver_model import get_all_drivers, add_driver, update_driver, delete_driver


def list_drivers():
    return get_all_drivers()


def add_driver_controller(name, license_number, phone, status, assigned_vehicle_id):
    add_driver(name, license_number, phone, status, assigned_vehicle_id)


def update_driver_controller(id, name, license_number, phone, status, assigned_vehicle_id):
    update_driver(id, name, license_number, phone, status, assigned_vehicle_id)


def delete_driver_controller(id):
    delete_driver(id)
