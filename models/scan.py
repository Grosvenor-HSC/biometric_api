# biometric_api/models/scan.py

from pydantic import BaseModel

class ScanIn(BaseModel):
    enrollmentId: int
    confidence: float
    employeeName: str
    clientLocalTime: str


class ScanOut(BaseModel):
    action: str
