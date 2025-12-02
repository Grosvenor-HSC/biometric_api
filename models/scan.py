from pydantic import BaseModel

class ScanIn(BaseModel):
    enrollmentId: int
    confidence: float
    employeeName: str
    siteId: str
    deviceId: str
    clientLocalTime: str | None = None


class ScanOut(BaseModel):
    action: str
