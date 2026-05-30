from views.common import TablePage
from controllers.schedule_controller import list_schedules


class TripStatusPage(TablePage):
    def __init__(self):
        columns = ['ID', 'Origin', 'Destination', 'Vehicle', 'Driver', 'Departure', 'Arrival', 'Status']
        rows = list_schedules()
        super().__init__('Trip Status', 'Check the status of current and upcoming trips.', columns, rows)
