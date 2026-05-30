from models.schedule_model import get_all_schedules, get_schedules_for_driver


def list_schedules():
    return get_all_schedules()


def list_schedules_for_driver(driver_id):
    return get_schedules_for_driver(driver_id)
