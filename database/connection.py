import pyodbc

from config import build_connection_string

CONNECTION_STRING = build_connection_string()


def get_connection(autocommit: bool = False):
    return pyodbc.connect(CONNECTION_STRING, autocommit=autocommit)
