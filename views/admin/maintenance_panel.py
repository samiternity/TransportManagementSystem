from views.common import TablePage
from controllers.maintenance_controller import list_maintenance_records


class MaintenancePanelPage(TablePage):
    def __init__(self):
        columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
        rows = list_maintenance_records()
        super().__init__('Maintenance Panel', 'Review maintenance work orders and status.', columns, rows)

    def refresh(self):
        self.update_table(list_maintenance_records())
