# biometric_api/models/employee.py

from pydantic import BaseModel

class EmployeeRecord(BaseModel):
    id: int
    ref: str
    name: str
