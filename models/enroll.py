from pydantic import BaseModel

class EnrollIn(BaseModel):
    siteId: str
    deviceId: str
    employeeName: str
    templateBase64: str
    clientLocalTime: str | None = None

class EnrollOut(BaseModel):
    enrollmentId: int
    enrollmentIdFormatted: str
    employeeRef: str
    status: str = "OK"

class ReenrolIn(BaseModel):
    enrollmentId: int
    templateBase64: str
    clientLocalTime: str | None = None
    siteId: str
    deviceId: str

class ReenrolOut(BaseModel):
    enrollmentId: int
    enrollmentIdFormatted: str
    employeeRef: str
    status: str = "OK"
