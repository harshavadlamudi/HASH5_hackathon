from fastapi import APIRouter, HTTPException
from typing import List
from app.models.patient import Patient, PatientSummary
from app.services.healthlake_service import healthlake_service

router = APIRouter()

@router.get("/patients", response_model=List[Patient])
async def get_patients():
    """Get all patients from HealthLake"""
    try:
        patients = healthlake_service.get_all_patients()
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get patient by ID"""
    try:
        patients = healthlake_service.get_all_patients()
        patient = next((p for p in patients if p['id'] == patient_id), None)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients/{patient_id}/summary", response_model=PatientSummary)
async def get_patient_summary(patient_id: str):
    """Get comprehensive patient summary"""
    try:
        summary = healthlake_service.get_patient_summary(patient_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
