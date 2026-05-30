import os
import pathlib

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
THEME_FILE = PROJECT_DIR / 'assets' / 'styles' / 'theme.qss'

MSSQL_DRIVER = os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')
MSSQL_SERVER = os.getenv('MSSQL_SERVER', 'localhost\\SQLEXPRESS')
MSSQL_DATABASE = os.getenv('MSSQL_DATABASE', 'TransportDB')
MSSQL_TRUSTED_CONNECTION = os.getenv('MSSQL_TRUSTED_CONNECTION', 'yes').strip().lower() in ('1', 'true', 'yes', 'y')
MSSQL_USERNAME = os.getenv('MSSQL_USERNAME', '')
MSSQL_PASSWORD = os.getenv('MSSQL_PASSWORD', '')


def build_connection_string(database=None):
    if database is None:
        database = MSSQL_DATABASE

    parts = [
        f'DRIVER={{{MSSQL_DRIVER}}}',
        f'SERVER={MSSQL_SERVER}',
        f'DATABASE={database}',
        'Encrypt=no',
        'TrustServerCertificate=yes',
    ]

    if MSSQL_TRUSTED_CONNECTION:
        parts.append('Trusted_Connection=yes')
    else:
        parts.append(f'UID={MSSQL_USERNAME}')
        parts.append(f'PWD={MSSQL_PASSWORD}')

    return ';'.join(parts) + ';'
