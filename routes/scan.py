# biometric_api/routes/scan.py

import socket
import logging
from fastapi import APIRouter, Depends

from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.scan import ScanIn, ScanOut

logger = logging.getLogger(__name__)

# IMPORTANT:
# - This router prefix is "/scan"
# - In main.py you include it with prefix="/api"
#   -> final path is POST /api/scan
router = APIRouter(prefix="/scan", tags=["scan"])

# Defaults are now decided server-side
DEFAULT_SITE_ID = "SITE-001"
DEFAULT_DEVICE_ID = socket.gethostname()


@router.post("", response_model=ScanOut)
def scan(req: ScanIn, ok=Depends(require_signed_request)):
    """
    Record a scan event for an existing enrollment.

    Behaviour:
      - Looks at the last BiometricEvents row for this EnrollmentId
        to decide whether the next event is "IN" or "OUT".
      - Inserts a new row into dbo.BiometricEvents with:
          EnrollmentId, SiteId, DeviceId, Action, Confidence,
          EmployeeName, ClientLocalTime
      - SiteId / DeviceId are filled from DEFAULT_* on the server.
    """
    cn = get_conn()
    cur = cn.cursor()

    enrollment_id = req.enrollmentId

    # Determine next action based on last event
    cur.execute(
        """
        SELECT TOP 1 Action
        FROM dbo.BiometricEvents
        WHERE EnrollmentId = ?
        ORDER BY Id DESC
        """,
        (enrollment_id,),
    )

    last = cur.fetchone()
    next_action = "IN" if not last or last[0] == "OUT" else "OUT"

    logger.info(
        "scan: enrollment_id=%s last_action=%s next_action=%s confidence=%s",
        enrollment_id,
        last[0] if last else None,
        next_action,
        req.confidence,
    )

    # Insert new event
    cur.execute(
        """
        INSERT INTO dbo.BiometricEvents
        (EnrollmentId, Action, Confidence, EmployeeName, ClientLocalTime)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            enrollment_id,
            next_action,
            req.confidence,
            req.employeeName,
            req.clientLocalTime,
        ),
    )

    cn.commit()

    return {"action": next_action}
