# biometric_api/routes/template.py
import base64
import logging
from fastapi import APIRouter, Depends, HTTPException
from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.template import TemplateOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/template", tags=["template"])

@router.get("/{enrollment_id}", response_model=TemplateOut)
def get_template(enrollment_id: int, ok=Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    cur.execute("""
        SELECT 
            E.Id,
            E.EmployeeName,
            E.UpdatedAt,  -- datetime2(7)
            T.TemplateBlob
        FROM dbo.BiometricEnrollments E
        INNER JOIN dbo.FingerprintTemplates T ON T.EnrollmentId = E.Id
        WHERE E.Id = ?
    """, (enrollment_id,))

    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    eid, name, updated_at, blob = row

    if blob is None:
        raise HTTPException(status_code=404, detail="Template missing")

    logger.info(f"template.get_template: enrollment_id={eid} name={name!r} bytes={len(blob)}")

    template_b64 = base64.b64encode(blob).decode("ascii")

    return TemplateOut(
        enrollmentId=eid,
        employeeName=name,
        updatedAt=updated_at,
        templateBase64=template_b64,
    )
