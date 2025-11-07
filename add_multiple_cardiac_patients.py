import boto3
import json
import requests
import random
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from datetime import datetime, timedelta
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

# Patient data templates
PATIENTS = [
    {"given": ["Sarah", "Ann"], "family": "Johnson", "gender": "female", "birthDate": "1958-03-22", 
     "condition": "Atrial fibrillation", "snomed": "49436004", "hr": 110, "pr": 0, "qrs": 85, "qt": 380},
    
    {"given": ["Robert", "James"], "family": "Williams", "gender": "male", "birthDate": "1972-11-08",
     "condition": "Myocardial infarction", "snomed": "22298006", "hr": 95, "pr": 180, "qrs": 105, "qt": 440},
    
    {"given": ["Maria", "Elena"], "family": "Garcia", "gender": "female", "birthDate": "1965-07-15",
     "condition": "Heart failure", "snomed": "84114007", "hr": 88, "pr": 170, "qrs": 110, "qt": 450},
    
    {"given": ["David", "Lee"], "family": "Chen", "gender": "male", "birthDate": "1980-02-28",
     "condition": "Ventricular tachycardia", "snomed": "25569003", "hr": 145, "pr": 155, "qrs": 120, "qt": 320},
    
    {"given": ["Jennifer", "Marie"], "family": "Brown", "gender": "female", "birthDate": "1955-09-12",
     "condition": "Coronary artery disease", "snomed": "53741008", "hr": 72, "pr": 165, "qrs": 92, "qt": 415},
]

def create_patient_with_ecg(patient_data):
    """Create patient with cardiac condition and ECG"""
    
    # Create Patient
    patient = {
        "resourceType": "Patient",
        "name": [{
            "use": "official",
            "family": patient_data["family"],
            "given": patient_data["given"]
        }],
        "gender": patient_data["gender"],
        "birthDate": patient_data["birthDate"],
        "address": [{
            "line": [f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar'])} St"],
            "city": random.choice(["Seattle", "Portland", "San Francisco", "Los Angeles"]),
            "state": random.choice(["WA", "OR", "CA"]),
            "postalCode": f"{random.randint(90000, 99999)}",
            "country": "US"
        }]
    }
    
    patient_result = post_to_healthlake(patient)
    patient_id = patient_result['id']
    print(f"  Created Patient: {patient_data['given'][0]} {patient_data['family']} ({patient_id})")
    
    # Create Condition
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
                "code": patient_data["snomed"],
                "display": patient_data["condition"]
            }],
            "text": patient_data["condition"]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "onsetDateTime": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    condition_result = post_to_healthlake(condition)
    print(f"    - Condition: {patient_data['condition']}")
    
    # Create ECG Observation
    components = [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
            "valueQuantity": {"value": patient_data["hr"], "unit": "beats/minute", "system": "http://unitsofmeasure.org", "code": "/min"}
        }
    ]
    
    if patient_data["pr"] > 0:
        components.append({
            "code": {"coding": [{"system": "http://loinc.org", "code": "8625-6", "display": "PR interval"}]},
            "valueQuantity": {"value": patient_data["pr"], "unit": "ms", "system": "http://unitsofmeasure.org", "code": "ms"}
        })
    
    components.extend([
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8633-0", "display": "QRS duration"}]},
            "valueQuantity": {"value": patient_data["qrs"], "unit": "ms", "system": "http://unitsofmeasure.org", "code": "ms"}
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8634-8", "display": "QT interval"}]},
            "valueQuantity": {"value": patient_data["qt"], "unit": "ms", "system": "http://unitsofmeasure.org", "code": "ms"}
        }
    ])
    
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
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueString": f"ECG findings consistent with {patient_data['condition']}",
        "component": components
    }
    
    observation_result = post_to_healthlake(observation)
    observation_id = observation_result['id']
    print(f"    - ECG: HR={patient_data['hr']}, QRS={patient_data['qrs']}, QT={patient_data['qt']}")
    
    # Create Diagnostic Report
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
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "result": [{"reference": f"Observation/{observation_id}"}],
        "conclusion": f"ECG consistent with {patient_data['condition']}. Recommend cardiology follow-up."
    }
    
    report_result = post_to_healthlake(report)
    print(f"    - Report: {report_result['id']}\n")
    
    return patient_id

if __name__ == "__main__":
    print("=" * 70)
    print("ADDING MULTIPLE CARDIAC PATIENTS WITH ECG DATA")
    print("=" * 70)
    
    created_patients = []
    
    for i, patient_data in enumerate(PATIENTS, 1):
        print(f"\n{i}. Creating patient {patient_data['given'][0]} {patient_data['family']}...")
        try:
            patient_id = create_patient_with_ecg(patient_data)
            created_patients.append({
                "name": f"{patient_data['given'][0]} {patient_data['family']}",
                "id": patient_id,
                "condition": patient_data['condition']
            })
        except Exception as e:
            print(f"   ERROR: {str(e)}\n")
    
    print("=" * 70)
    print(f"SUCCESS! Created {len(created_patients)} cardiac patients with ECG data")
    print("=" * 70)
    
    print("\nPatients Created:")
    for p in created_patients:
        print(f"  - {p['name']}: {p['condition']} (ID: {p['id']})")
    
    print("\nYou can now query:")
    print("  - 'Show me all cardiac patients'")
    print("  - 'What ECG data is available?'")
    print("  - 'Show me patients with atrial fibrillation'")
    print("  - 'List all heart conditions'")
