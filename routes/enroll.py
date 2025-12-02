import base64
import logging
from fastapi import APIRouter, Depends
from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.enroll import EnrollIn, EnrollOut, ReenrolIn, ReenrolOut
from fastapi import HTTPException
import base64

logger = logging.getLogger(__name__)

# ⚠ DO NOT add prefix="/api" here
router = APIRouter(tags=["enrol"])


@router.post("/enrol", response_model=EnrollOut)
def enrol(req: EnrollIn, _: bool = Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    # 1) Insert only EmployeeName because that is all the table supports
    cur.execute("""
        INSERT INTO dbo.BiometricEnrollments (EmployeeName)
        OUTPUT inserted.Id
        VALUES (?)
    """, (req.employeeName,))

    enrollment_id = cur.fetchone()[0]

    # 2) Store the fingerprint template
    cur.execute("""
        INSERT INTO dbo.FingerprintTemplates (EnrollmentId, TemplateBlob)
        VALUES (?, ?)
    """, (
        enrollment_id,
        base64.b64decode(req.templateBase64)
    ))

    cn.commit()

    # 3) Create a virtual employee reference to return to the client
    employee_ref = f"ENR-{enrollment_id:07d}"

    return {
        "enrollmentId": enrollment_id,
        "enrollmentIdFormatted": f"{enrollment_id:07d}",
        "employeeRef": employee_ref,
        "status": "OK"
    }


@router.post("/reenrol", response_model=ReenrolOut)
def reenrol(req: ReenrolIn, _: bool = Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    # 1) Ensure the enrollment exists
    cur.execute("""
        SELECT EmployeeName
        FROM dbo.BiometricEnrollments
        WHERE Id = ?
    """, (req.enrollmentId,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="enrollment not found")

    employee_name = row[0]

    # 2) Replace existing templates for this enrollment
    cur.execute("""
        DELETE FROM dbo.FingerprintTemplates
        WHERE EnrollmentId = ?
    """, (req.enrollmentId,))

    cur.execute("""
        INSERT INTO dbo.FingerprintTemplates (EnrollmentId, TemplateBlob)
        VALUES (?, ?)
    """, (
        req.enrollmentId,
        base64.b64decode(req.templateBase64)
    ))

    cn.commit()

    employee_ref = f"ENR-{req.enrollmentId:07d}"

    return {
        "enrollmentId": req.enrollmentId,
        "enrollmentIdFormatted": f"{req.enrollmentId:07d}",
        "employeeRef": employee_ref,
        "status": "OK",
    }