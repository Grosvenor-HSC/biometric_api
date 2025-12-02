from fastapi import APIRouter, Depends
from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.employee import EmployeeRecord

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.get("/search")
def search(q: str, ok=Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    cur.execute("""
        SELECT EmployeeRef, EmployeeName
        FROM dbo.BiometricEnrollments
        WHERE EmployeeName LIKE ?
        ORDER BY EmployeeName
    """, (f"%{q}%",))

    return [{"ref": r[0], "name": r[1]} for r in cur.fetchall()]
