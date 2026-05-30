from views.common import TablePage
from controllers.maintenance_controller import list_maintenance_records


class RepairSchedulerPage(TablePage):
    def __init__(self):
        columns = ['ID', 'Vehicle', 'Issue', 'Status', 'Scheduled', 'Completed']
        rows = list_maintenance_records()
        super().__init__('Repair Scheduler', 'Schedule repairs and track maintenance timelines.', columns, rows)
