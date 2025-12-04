from datetime import datetime
from pydantic import BaseModel

class TemplateOut(BaseModel):
    enrollmentId: int
    employeeName: str
    updatedAt: datetime | None   # <-- MUST be datetime
    templateBase64: str
