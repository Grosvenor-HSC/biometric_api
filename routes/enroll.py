# biometric_api/routes/enroll.py

import base64
import logging

from fastapi import APIRouter, Depends, HTTPException

from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.enroll import EnrollIn, EnrollOut, ReenrolIn, ReenrolOut

logger = logging.getLogger(__name__)

# NOTE: main.py includes this router with prefix="/api"
# so do NOT put "/api" here.
router = APIRouter(tags=["enrol"])


@router.post("/enrol", response_model=EnrollOut)
def enrol(req: EnrollIn, _: bool = Depends(require_signed_request)):
    """
    First-time enrolment:
    - insert a new row into BiometricEnrollments
    - insert the initial template into FingerprintTemplates
    """
    cn = get_conn()
    cur = cn.cursor()

    logger.info("Enrolling NEW employee '%s'", req.employeeName)

    # Insert only EmployeeName (plus timestamps if your table has them)
    cur.execute("""
        INSERT INTO [BiometricClock].[dbo].[BiometricEnrollments] (EmployeeName, CreatedAt)
        OUTPUT inserted.Id
        VALUES (?, SYSDATETIME())
    """, (req.employeeName,))

    enrollment_id = cur.fetchone()[0]

    # Store the fingerprint template
    cur.execute("""
        INSERT INTO [BiometricClock].[dbo].[FingerprintTemplates] (EnrollmentId, TemplateBlob)
        VALUES (?, ?)
    """, (
        enrollment_id,
        base64.b64decode(req.templateBase64),
    ))

    cn.commit()

    employee_ref = f"ENR-{enrollment_id:07d}"

    return {
        "enrollmentId": enrollment_id,
        "enrollmentIdFormatted": f"{enrollment_id:07d}",
        "employeeRef": employee_ref,
        "status": "OK",
    }


@router.post("/reenrol", response_model=ReenrolOut)
def reenrol(req: ReenrolIn, _: bool = Depends(require_signed_request)):
    """
    Re-enrolment:
    - validate the enrollmentId exists
    - delete existing templates for that enrollment
    - insert the new template
    - update UpdatedAt on the enrollment
    """
    cn = get_conn()
    cur = cn.cursor()

    # 1) Ensure the enrollment exists
    cur.execute("""
        SELECT EmployeeName
        FROM [BiometricClock].[dbo].[BiometricEnrollments]
        WHERE Id = ?
    """, (req.enrollmentId,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="enrollment not found")

    employee_name = row[0]
    logger.info("Re-enrolling Id=%s (%s)", req.enrollmentId, employee_name)

    # 2) Replace existing templates for this enrollment
    cur.execute("""
        DELETE FROM [BiometricClock].[dbo].[FingerprintTemplates]
        WHERE EnrollmentId = ?
    """, (req.enrollmentId,))

    cur.execute("""
        INSERT INTO [BiometricClock].[dbo].[FingerprintTemplates] (EnrollmentId, TemplateBlob)
        VALUES (?, ?)
    """, (
        req.enrollmentId,
        base64.b64decode(req.templateBase64),
    ))

    # 3) Optional: bump UpdatedAt
    cur.execute("""
        UPDATE [BiometricClock].[dbo].[BiometricEnrollments]
        SET UpdatedAt = SYSDATETIME()
        WHERE Id = ?
    """, (req.enrollmentId,))

    cn.commit()

    employee_ref = f"ENR-{req.enrollmentId:07d}"

    return {
        "enrollmentId": req.enrollmentId,
        "enrollmentIdFormatted": f"{req.enrollmentId:07d}",
        "employeeRef": employee_ref,
        "status": "OK",
    }
