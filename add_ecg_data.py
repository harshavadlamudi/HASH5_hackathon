import boto3
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'
REGION = 'us-west-2'

def post_to_healthlake(resource):
    """Post FHIR resource to HealthLake"""
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    resource_type = resource['resourceType']
    url = f"{endpoint}{resource_type}"
    
    request = AWSRequest(method='POST', url=url, data=json.dumps(resource), 
                        headers={'Content-Type': 'application/fhir+json'})
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    response = requests.post(url, data=json.dumps(resource), headers=dict(request.headers))
    response.raise_for_status()
    return response.json()

def create_cardiac_patient():
    """Create a patient with cardiac condition"""
    patient = {
        "resourceType": "Patient",
        "name": [{
            "use": "official",
            "family": "Smith",
            "given": ["John", "Michael"]
        }],
        "gender": "male",
        "birthDate": "1965-08-15",
        "address": [{
            "line": ["123 Heart St"],
            "city": "Seattle",
            "state": "WA",
            "postalCode": "98101",
            "country": "US"
        }]
    }
    
    result = post_to_healthlake(patient)
    patient_id = result['id']
    print(f"Created Patient: {patient_id}")
    return patient_id

def create_cardiac_condition(patient_id):
    """Create cardiac condition for patient"""
    condition = {
        "resourceType": "Condition",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": "confirmed"
            }]
        },
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "53741008",
                "display": "Coronary artery disease"
            }],
            "text": "Coronary artery disease"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "onsetDateTime": "2024-06-15T00:00:00Z",
        "recordedDate": "2024-06-15T00:00:00Z"
    }
    
    result = post_to_healthlake(condition)
    condition_id = result['id']
    print(f"Created Condition: {condition_id}")
    return condition_id

def create_ecg_observation(patient_id):
    """Create ECG observation with measurements"""
    observation = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "procedure",
                "display": "Procedure"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "11524-6",
                "display": "EKG study"
            }],
            "text": "12-Lead ECG"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueString": "Normal sinus rhythm with occasional PVCs",
        "interpretation": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "N",
                "display": "Normal"
            }]
        }],
        "component": [
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate"
                    }]
                },
                "valueQuantity": {
                    "value": 75,
                    "unit": "beats/minute",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min"
                }
            },
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8625-6",
                        "display": "PR interval"
                    }]
                },
                "valueQuantity": {
                    "value": 165,
                    "unit": "ms",
                    "system": "http://unitsofmeasure.org",
                    "code": "ms"
                }
            },
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8633-0",
                        "display": "QRS duration"
                    }]
                },
                "valueQuantity": {
                    "value": 95,
                    "unit": "ms",
                    "system": "http://unitsofmeasure.org",
                    "code": "ms"
                }
            },
            {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8634-8",
                        "display": "QT interval"
                    }]
                },
                "valueQuantity": {
                    "value": 410,
                    "unit": "ms",
                    "system": "http://unitsofmeasure.org",
                    "code": "ms"
                }
            }
        ]
    }
    
    result = post_to_healthlake(observation)
    observation_id = result['id']
    print(f"Created ECG Observation: {observation_id}")
    return observation_id

def create_ecg_diagnostic_report(patient_id, observation_id):
    """Create diagnostic report for ECG"""
    report = {
        "resourceType": "DiagnosticReport",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": "CG",
                "display": "Cardiology"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "11524-6",
                "display": "EKG study"
            }],
            "text": "12-Lead Electrocardiogram"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "result": [{
            "reference": f"Observation/{observation_id}"
        }],
        "conclusion": "Normal sinus rhythm with occasional premature ventricular contractions. No acute ST-T wave changes. Recommend follow-up in 6 months."
    }
    
    result = post_to_healthlake(report)
    report_id = result['id']
    print(f"Created Diagnostic Report: {report_id}")
    return report_id

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING CARDIAC PATIENT WITH ECG DATA")
    print("=" * 60)
    
    try:
        # Step 1: Create patient
        print("\n1. Creating cardiac patient...")
        patient_id = create_cardiac_patient()
        
        # Step 2: Create cardiac condition
        print("\n2. Creating cardiac condition...")
        condition_id = create_cardiac_condition(patient_id)
        
        # Step 3: Create ECG observation
        print("\n3. Creating ECG observation...")
        observation_id = create_ecg_observation(patient_id)
        
        # Step 4: Create diagnostic report
        print("\n4. Creating ECG diagnostic report...")
        report_id = create_ecg_diagnostic_report(patient_id, observation_id)
        
        print("\n" + "=" * 60)
        print("SUCCESS! Cardiac patient with ECG data created")
        print("=" * 60)
        print(f"\nPatient ID: {patient_id}")
        print(f"Condition ID: {condition_id}")
        print(f"ECG Observation ID: {observation_id}")
        print(f"Diagnostic Report ID: {report_id}")
        
        print("\nYou can now query:")
        print(f"- 'Show me ECG data for patient {patient_id}'")
        print(f"- 'What are the ECG results?'")
        print(f"- 'Show me cardiac patients'")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
