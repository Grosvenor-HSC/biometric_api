from pydantic import BaseModel

class EmployeeRecord(BaseModel):
    ref: str
    name: str
