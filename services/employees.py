# employees.py — generated placeholder
import pyodbc
from typing import List, Tuple

def search_employees(cnx: pyodbc.Connection, query: str) -> List[Tuple[str, str]]:
    q = f"%{query.strip().lower()}%"
    sql = """
    SELECT TOP 25 EmployeeRef, EmployeeName
    FROM dbo.BiometricEnrollments
    WHERE LOWER(EmployeeRef) LIKE ? OR LOWER(EmployeeName) LIKE ?
    ORDER BY EmployeeName;
    """
    with cnx.cursor() as cur:
        cur.execute(sql, q, q)
        return [(r[0], r[1]) for r in cur.fetchall()]
