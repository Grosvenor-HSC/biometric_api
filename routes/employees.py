from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from biometric_api.auth import require_signed_request
from biometric_api.db import get_conn
from biometric_api.models.employee import EmployeeRecord

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["employees"])



@router.get("/search")
def search(
    q: str = Query("", min_length=0),   # allow empty
    ok=Depends(require_signed_request),
):
    q = (q or "").strip()
    logger.info("employees.search: start q=%r", q)

    cn = get_conn()
    cur = cn.cursor()

    if q:
        # Filter by name if query provided
        cur.execute(
            """
            SELECT Id,
                   EmployeeName AS Name
            FROM dbo.BiometricEnrollments
            WHERE EmployeeName LIKE '%' + ? + '%'
            ORDER BY EmployeeName, Id
            """,
            (q,),
        )
    else:
        # Empty query -> return all enrolled users
        cur.execute(
            """
            SELECT Id,
                   EmployeeName AS Name
            FROM dbo.BiometricEnrollments
            ORDER BY EmployeeName, Id
            """
        )

    rows = cur.fetchall()
    logger.info("employees.search: rows=%d", len(rows))

    return [
        {
            "id": row[0],
            "ref": f"ENR-{row[0]:07d}",
            "name": row[1],
        }
        for row in rows
    ]


@router.delete("/{enrollment_id}")
def delete_enrollment(enrollment_id: int, ok=Depends(require_signed_request)):
    cn = get_conn()
    cur = cn.cursor()

    # Check it exists
    cur.execute(
        """
        SELECT COUNT(*)
        FROM [BiometricClock].[dbo].[BiometricEnrollments]
        WHERE Id = ?
        """,
        (enrollment_id,),
    )
    if cur.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="enrollment not found")

    # Delete templates first
    cur.execute(
        """
        DELETE FROM [BiometricClock].[dbo].[FingerprintTemplates]
        WHERE EnrollmentId = ?
        """,
        (enrollment_id,),
    )

    # Delete the enrollment row
    cur.execute(
        """
        DELETE FROM [BiometricClock].[dbo].[BiometricEnrollments]
        WHERE Id = ?
        """,
        (enrollment_id,),
    )

    cn.commit()
    logger.info("employees.delete_enrollment: deleted enrollment_id=%s", enrollment_id)

    return {"status": "OK"}
