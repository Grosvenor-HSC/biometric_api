from fastapi import APIRouter, Depends
from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.scan import ScanIn, ScanOut

router = APIRouter(prefix="/api", tags=["scan"])

@router.post("/scan", response_model=ScanOut)
def scan(req: ScanIn, ok=Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    # Determine IN/OUT by last event
    cur.execute("""
        SELECT TOP 1 Action
        FROM dbo.BiometricEvents
        WHERE EnrollmentId = ?
        ORDER BY Id DESC
    """, (req.enrollmentId,))

    last = cur.fetchone()
    next_action = "IN" if not last or last[0] == "OUT" else "OUT"

    cur.execute("""
        INSERT INTO dbo.BiometricEvents
        (EnrollmentId, SiteId, DeviceId, Action, Confidence, EmployeeName, ClientLocalTime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        req.enrollmentId,
        req.siteId,
        req.deviceId,
        next_action,
        req.confidence,
        req.employeeName,
        req.clientLocalTime
    ))

    cn.commit()
    return {"action": next_action}
