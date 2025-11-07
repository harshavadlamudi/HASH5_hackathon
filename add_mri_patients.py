import boto3
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

load_dotenv()

REGION = 'us-west-2'
DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'

def create_resource(resource):
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    url = f"{endpoint}{resource['resourceType']}"
    data = json.dumps(resource)
    
    request = AWSRequest(method='POST', url=url, data=data, headers={'Content-Type': 'application/fhir+json'})
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    response = requests.post(url, data=data, headers=dict(request.headers))
    return response

# MRI Patients Data
mri_patients = [
    {
        "name": {"given": ["Michael"], "family": "Anderson"},
        "gender": "male",
        "birthDate": "1965-03-15",
        "condition": "Brain tumor (glioblastoma)",
        "mri_type": "Brain MRI",
        "findings": "4.2 cm mass in right frontal lobe with surrounding edema and mass effect"
    },
    {
        "name": {"given": ["Patricia"], "family": "Martinez"},
        "gender": "female",
        "birthDate": "1972-08-22",
        "condition": "Multiple sclerosis",
        "mri_type": "Brain and Spine MRI",
        "findings": "Multiple periventricular white matter lesions consistent with demyelinating disease"
    },
    {
        "name": {"given": ["James"], "family": "Thompson"},
        "gender": "male",
        "birthDate": "1958-11-30",
        "condition": "Lumbar disc herniation",
        "mri_type": "Lumbar Spine MRI",
        "findings": "L4-L5 disc herniation with nerve root compression"
    },
    {
        "name": {"given": ["Linda"], "family": "Davis"},
        "gender": "female",
        "birthDate": "1980-05-18",
        "condition": "Meniscal tear",
        "mri_type": "Knee MRI",
        "findings": "Medial meniscus tear with joint effusion"
    },
    {
        "name": {"given": ["Robert"], "family": "Wilson"},
        "gender": "male",
        "birthDate": "1955-09-07",
        "condition": "Stroke (ischemic)",
        "mri_type": "Brain MRI with DWI",
        "findings": "Acute infarct in left middle cerebral artery territory"
    }
]

def main():
    for idx, patient_data in enumerate(mri_patients, 1):
        print(f"\n[{idx}/5] Creating MRI patient: {patient_data['name']['given'][0]} {patient_data['name']['family']}")
        
        # Create Patient
        patient = {
            "resourceType": "Patient",
            "name": [patient_data["name"]],
            "gender": patient_data["gender"],
            "birthDate": patient_data["birthDate"]
        }
        
        patient_response = create_resource(patient)
        patient_json = patient_response.json()
        patient_id = patient_json['id']
        print(f"  Patient ID: {patient_id}")
        
        # Create Condition
        condition = {
            "resourceType": "Condition",
            "subject": {"reference": f"Patient/{patient_id}", "display": f"{patient_data['name']['given'][0]} {patient_data['name']['family']}"},
            "code": {"text": patient_data["condition"]},
            "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
            "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        create_resource(condition)
        print(f"  Condition: {patient_data['condition']}")
        
        # Create DiagnosticReport for MRI
        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "24627-2",
                    "display": "MRI Study"
                }],
                "text": patient_data["mri_type"]
            },
            "subject": {"reference": f"Patient/{patient_id}", "display": f"{patient_data['name']['given'][0]} {patient_data['name']['family']}"},
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "conclusion": patient_data["findings"],
            "presentedForm": [{
                "contentType": "text/plain",
                "data": patient_data["findings"],
                "title": f"{patient_data['mri_type']} Report"
            }]
        }
        
        create_resource(diagnostic_report)
        print(f"  MRI Report: {patient_data['mri_type']}")
        print(f"  Findings: {patient_data['findings']}")
    
    print("\n[OK] Successfully created 5 MRI patients with diagnostic reports!")
    print("\nPatient Summary:")
    print("1. Michael Anderson - Brain tumor (Brain MRI)")
    print("2. Patricia Martinez - Multiple sclerosis (Brain/Spine MRI)")
    print("3. James Thompson - Lumbar disc herniation (Spine MRI)")
    print("4. Linda Davis - Meniscal tear (Knee MRI)")
    print("5. Robert Wilson - Stroke (Brain MRI with DWI)")

if __name__ == "__main__":
    main()
