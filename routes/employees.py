# biometric_api/routes/employees.py

from fastapi import APIRouter, Depends
from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.get("/search")
def search(q: str, ok=Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    # ADDED: "Id" to the SELECT statement
    cur.execute("""
        SELECT Id, EmployeeRef, EmployeeName
        FROM dbo.BiometricEnrollments
        WHERE EmployeeName LIKE ?
        ORDER BY EmployeeName
    """, (f"%{q}%",))

    # Return the ID so the C# app can use it for re-enrol/scan
    return [{"id": r[0], "ref": r[1], "name": r[2]} for r in cur.fetchall()]