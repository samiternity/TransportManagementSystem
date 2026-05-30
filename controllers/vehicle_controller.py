from models.vehicle_model import get_all_vehicles, add_vehicle, update_vehicle, delete_vehicle


def list_vehicles():
    return get_all_vehicles()


def add_vehicle_controller(plate_number, make, model, year, status, mileage):
    add_vehicle(plate_number, make, model, year, status, mileage)


def update_vehicle_controller(id, plate_number, make, model, year, status, mileage):
    update_vehicle(id, plate_number, make, model, year, status, mileage)


def delete_vehicle_controller(id):
    delete_vehicle(id)
