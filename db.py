import pyodbc
import os

def get_conn():
    conn_str = os.getenv("BIOMETRIC_SQL_CONN")
    return pyodbc.connect(conn_str)
