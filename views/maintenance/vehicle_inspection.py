from views.common import TablePage
from controllers.maintenance_controller import list_maintenance_records


class VehicleInspectionPage(TablePage):
    def __init__(self):
        columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
        rows = list_maintenance_records()
        super().__init__('Vehicle Inspection', 'Inspect vehicles and verify service completion.', columns, rows)
