from models.assignment_model import AssignmentModel
from models.vehicle_model import VehicleModel
from models.driver_model import DriverModel
from services.payment_service import PaymentService
from database.db_handler import DatabaseHandler
from datetime import datetime, timedelta

class AssignmentService:
    def __init__(self):
        self.assignment_model = AssignmentModel()
        self.vehicle_model = VehicleModel()
        self.payment_service = PaymentService()
        self.db = DatabaseHandler()

    def create_linked_assignment(self, vehicle_id, driver_id, route_id, start_date, dep_time_str=None, arr_time_str=None, fare=500.0):
        """
        Enforces the Transport Assignment Flow:
        1. Check vehicle availability and status.
        2. Check driver availability.
        3. Prevent duplicate active assignments.
        4. Create assignment and auto-generate schedule.
        """
        # 1. Validate Vehicle
        vehicle = self.db.execute_query(
            "SELECT status FROM vehicles WHERE id = ?", (vehicle_id,), fetch=True
        )
        if not vehicle or vehicle[0][0] != 'Available':
            raise ValueError("Selected vehicle is not available for assignment.")

        # 2. Validate Driver
        driver = self.db.execute_query(
            "SELECT status FROM drivers WHERE id = ?", (driver_id,), fetch=True
        )
        if not driver or driver[0][0] != 'Available':
            raise ValueError("Selected driver is not available for assignment.")

        # 3. Check for duplicates
        existing = self.db.execute_scalar(
            "SELECT COUNT(*) FROM assignments WHERE vehicle_id = ? AND driver_id = ? AND route_id = ? AND status = 'Active'",
            (vehicle_id, driver_id, route_id)
        )
        if existing > 0:
            raise ValueError("An active assignment with this configuration already exists.")

        # 4. Create Assignment and update statuses
        success = self.assignment_model.create_assignment(vehicle_id, driver_id, route_id, start_date, fare)
        
        if success:
            # Update Driver status and assigned vehicle
            self.db.execute_query(
                "UPDATE drivers SET status = 'On Trip', assigned_vehicle_id = ? WHERE id = ?",
                (vehicle_id, driver_id)
            )
            # Update Vehicle status
            self.db.execute_query(
                "UPDATE vehicles SET status = 'In Service' WHERE id = ?",
                (vehicle_id,)
            )

            # 5. Auto-generate Schedule safely
            assignment_id = self.db.execute_scalar(
                "SELECT id FROM assignments WHERE vehicle_id = ? AND driver_id = ? AND route_id = ? AND status = 'Active'",
                (vehicle_id, driver_id, route_id)
            )
            self._generate_single_schedule(assignment_id, start_date, dep_time_str, arr_time_str)
            return True
        return False

    def _generate_single_schedule(self, assignment_id, start_date, dep_time_str, arr_time_str):
        """Generates a single schedule entry for the assignment."""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Parse times or use defaults
        if dep_time_str:
            dep_t = datetime.strptime(dep_time_str, '%H:%M').time()
            dep_time = datetime.combine(start_dt.date(), dep_t)
        else:
            dep_time = start_dt.replace(hour=8, minute=0)

        if arr_time_str:
            arr_t = datetime.strptime(arr_time_str, '%H:%M').time()
            arr_time = datetime.combine(start_dt.date(), arr_t)
        else:
            arr_time = start_dt.replace(hour=12, minute=0)
            
        self.db.execute_query(
            "INSERT INTO schedules (assignment_id, departure_time, arrival_time, status) VALUES (?, ?, ?, 'Scheduled')",
            (assignment_id, dep_time, arr_time)
        )

    def allocate_passenger(self, assignment_id, passenger_id):
        """Allocates a passenger and uses the assignment's custom fare for billing."""
        details = self.assignment_model.get_assignment_details(assignment_id)
        if not details:
            raise ValueError("Assignment not found.")
            
        capacity = details[4]
        fare = details[6] # Retrieve the monthly_fare stored in assignments
        
        current_bookings = self.db.execute_scalar(
            "SELECT COUNT(*) FROM bookings WHERE assignment_id = ? AND status = 'Confirmed'",
            (assignment_id,)
        )
        
        if current_bookings >= capacity:
            raise ValueError("Vehicle capacity reached for this assignment.")
            
        # Create booking
        success = self.db.execute_query(
            "INSERT INTO bookings (passenger_id, assignment_id, booking_date, status) VALUES (?, ?, GETDATE(), 'Confirmed')",
            (passenger_id, assignment_id)
        )
        
        if success:
            # Automate Fee Generation using the assignment-specific fare
            now = datetime.now()
            month_year = now.strftime('%B %Y')
            due_date = (now + timedelta(days=7)).strftime('%Y-%m-%d')
            self.payment_service.automate_fee_generation(passenger_id, assignment_id, fare, month_year, due_date)
            
        return success
