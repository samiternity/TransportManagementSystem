from models.maintenance_model import MaintenanceModel

class MaintenanceService:
    def __init__(self):
        self.model = MaintenanceModel()

    def report_driver_issue(self, vehicle_id, description, driver_id):
        """Driver reports an issue, vehicle status updates automatically."""
        return self.model.report_issue(vehicle_id, description, driver_id)

    def schedule_maintenance(self, record_id, date_str):
        """Maintenance staff schedules a repair."""
        return self.model.schedule_repair(record_id, date_str)

    def resolve_maintenance(self, record_id, final_cost):
        """Repair completed, vehicle returns to service rotation."""
        return self.model.complete_repair(record_id, final_cost)
