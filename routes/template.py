from fastapi import APIRouter, Depends, HTTPException
from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn

router = APIRouter(prefix="/api", tags=["scan"])

@router.get("/template/{enrollmentId}")
def get_template(enrollmentId: int, ok=Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    # Fetch template + employee name
    cur.execute("""
        SELECT E.EmployeeName,
               T.TemplateBlob
        FROM dbo.BiometricEnrollments E
        INNER JOIN dbo.FingerprintTemplates T ON T.EnrollmentId = E.Id
        WHERE E.Id = ?
    """, (enrollmentId,))

    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Not found")

    return {
        "employeeName": row[0],
        "templateBase64": row[1].decode("latin1").encode("latin1").hex()
    }
