"""
Create user accounts with login credentials for drivers and passengers.
Usage: python create_accounts.py
"""
from database.db_handler import DatabaseHandler
from utils.hashing import hash_password


def create_driver_account(username, password, name, license_number, phone):
    """Create a driver with login credentials."""
    db = DatabaseHandler()
    pass_hash = hash_password(password)
    
    # 1. Create user account
    db.execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, pass_hash, 'Driver')
    )
    
    # 2. Get the user_id
    user_id = db.execute_scalar("SELECT id FROM users WHERE username = ?", (username,))
    
    # 3. Create driver record linked to user
    db.execute_query(
        "INSERT INTO drivers (user_id, name, license_number, phone, status) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, license_number, phone, 'Available')
    )
    
    print(f"Driver account created: {username} / {password}")


def create_passenger_account(username, password, name, phone):
    """Create a passenger/student with login credentials."""
    db = DatabaseHandler()
    pass_hash = hash_password(password)
    
    # 1. Create user account
    db.execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, pass_hash, 'Passenger')
    )
    
    # 2. Get the user_id
    user_id = db.execute_scalar("SELECT id FROM users WHERE username = ?", (username,))
    
    # 3. Create passenger record linked to user
    db.execute_query(
        "INSERT INTO passengers (user_id, name, phone, outstanding_balance) VALUES (?, ?, ?, ?)",
        (user_id, name, phone, 0.00)
    )
    
    print(f"Passenger account created: {username} / {password}")


if __name__ == '__main__':
    # Example: Create new accounts
    
    # New driver
    create_driver_account(
        username='driver02',
        password='Pass@123',
        name='Ali Hassan',
        license_number='DR-002',
        phone='+92 300 5556667'
    )
    
    # New student/passenger
    create_passenger_account(
        username='student02',
        password='Pass@123',
        name='Sarah Khan',
        phone='+92 333 7778889'
    )
    
    print("\nAccounts created successfully!")
