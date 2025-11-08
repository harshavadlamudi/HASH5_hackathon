from pydantic import BaseModel
from typing import List, Optional

class Patient(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    birthDate: Optional[str] = None

class PatientSummary(BaseModel):
    id: str
    name: str
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    conditions: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    has_ecg: bool = False
    mri_reports_count: int = 0
