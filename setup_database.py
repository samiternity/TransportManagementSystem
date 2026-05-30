import pathlib
import re
import pyodbc
from config import (
    MSSQL_DATABASE,
    MSSQL_DRIVER,
    MSSQL_SERVER,
    MSSQL_TRUSTED_CONNECTION,
    MSSQL_USERNAME,
    MSSQL_PASSWORD,
    build_connection_string,
)
from utils.hashing import hash_password
from database.db_handler import DatabaseHandler

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

def build_master_connection_string() -> str:
    parts = [
        f'DRIVER={{{MSSQL_DRIVER}}}',
        f'SERVER={MSSQL_SERVER}',
        'DATABASE=master',
        'Encrypt=no',
        'TrustServerCertificate=yes',
    ]
    if MSSQL_TRUSTED_CONNECTION:
        parts.append('Trusted_Connection=yes')
    else:
        parts.append(f'UID={MSSQL_USERNAME}')
        parts.append(f'PWD={MSSQL_PASSWORD}')
    return ';'.join(parts) + ';'

def create_database_if_missing():
    conn = pyodbc.connect(build_master_connection_string(), autocommit=True)
    cursor = conn.cursor()
    try:
        cursor.execute(f"IF DB_ID(N'{MSSQL_DATABASE}') IS NULL CREATE DATABASE [{MSSQL_DATABASE}]")
    finally:
        cursor.close()
        conn.close()

def split_batches(sql_text: str):
    return [batch.strip() for batch in re.split(r'^\s*GO\s*$', sql_text, flags=re.MULTILINE | re.IGNORECASE) if batch.strip()]

def create_schema():
    with open(_SCRIPT_DIR / 'database' / 'schema.sql', 'r', encoding='utf-8') as file:
        schema_sql = file.read()
    
    conn = pyodbc.connect(build_connection_string(), autocommit=False)
    cursor = conn.cursor()
    try:
        for batch in split_batches(schema_sql):
            cursor.execute(batch)
        conn.commit()
    except Exception as e:
        print(f"Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def seed_data():
    db = DatabaseHandler()
    default_password_hash = hash_password('Pass@123')
    seed_users = [
        ('admin', 'Administrator'),
        ('passenger01', 'Passenger'),
        ('maint01', 'Maintenance'),
        ('driver01', 'Driver'),
        ('driver02', 'Driver'),
        ('passenger02', 'Passenger'),
        ('passenger03', 'Passenger'),
        ('passenger04', 'Passenger'),
        ('passenger05', 'Passenger'),
        ('passenger06', 'Passenger'),
        ('passenger07', 'Passenger'),
        ('passenger08', 'Passenger'),
    ]

    for username, role in seed_users:
        db.execute_query(
            "IF NOT EXISTS (SELECT 1 FROM users WHERE username = ?) "
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, username, default_password_hash, role),
        )

    passenger_profiles = [
        ('passenger01', 'Seeded Passenger', ''),
    ]
    for uname, name, phone in passenger_profiles:
        user_id = db.execute_scalar("SELECT id FROM users WHERE username = ?", (uname,))
        if user_id is None:
            continue
        db.execute_query(
            "IF NOT EXISTS (SELECT 1 FROM passengers WHERE user_id = ?) "
            "INSERT INTO passengers (user_id, name, phone, outstanding_balance) VALUES (?, ?, ?, ?)",
            (user_id, user_id, name, phone, 0.00),
        )

def seed_demo_data():
    with open(_SCRIPT_DIR / 'database' / 'seed_data.sql', 'r', encoding='utf-8') as file:
        seed_sql = file.read()
    
    conn = pyodbc.connect(build_connection_string(), autocommit=False)
    cursor = conn.cursor()
    try:
        for batch in split_batches(seed_sql):
            cursor.execute(batch)
        conn.commit()
    except Exception as e:
        print(f"Error seeding demo data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    print('Checking database...')
    create_database_if_missing()
    print('Applying schema...')
    create_schema()
    print('Seeding login credentials...')
    seed_data()
    print('Seeding demo data...')
    seed_demo_data()
    print('System initialized successfully with demo data!')

if __name__ == '__main__':
    main()
