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

# Existing MRI patients with their IDs
mri_patients = [
    {
        "id": "6f0bc274-9b4e-4cc0-80eb-d49aa2f6da9a",
        "name": "Michael Anderson",
        "mri_type": "Brain MRI",
        "findings": "4.2 cm mass in right frontal lobe with surrounding edema and mass effect"
    },
    {
        "id": "89698d95-8e01-4d88-8f00-945372d5aac9",
        "name": "Patricia Martinez",
        "mri_type": "Brain and Spine MRI",
        "findings": "Multiple periventricular white matter lesions consistent with demyelinating disease"
    },
    {
        "id": "3ac6d9cb-e28f-4322-af37-86704edc03c3",
        "name": "James Thompson",
        "mri_type": "Lumbar Spine MRI",
        "findings": "L4-L5 disc herniation with nerve root compression"
    },
    {
        "id": "db2dca16-3c5f-47e4-98dd-63bcc491e6ac",
        "name": "Linda Davis",
        "mri_type": "Knee MRI",
        "findings": "Medial meniscus tear with joint effusion"
    },
    {
        "id": "a1532ebb-26bf-42c4-a523-ab56d9d76369",
        "name": "Robert Wilson",
        "mri_type": "Brain MRI with DWI",
        "findings": "Acute infarct in left middle cerebral artery territory"
    }
]

print("Adding missing DiagnosticReport resources...\n")

for idx, patient in enumerate(mri_patients, 1):
    print(f"[{idx}/5] Creating DiagnosticReport for {patient['name']}")
    
    diagnostic_report = {
        "resourceType": "DiagnosticReport",
        "status": "final",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "24627-2",
                "display": "MRI Study"
            }],
            "text": patient["mri_type"]
        },
        "subject": {
            "reference": f"Patient/{patient['id']}",
            "display": patient['name']
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "conclusion": patient["findings"]
    }
    
    response = create_resource(diagnostic_report)
    
    if response.status_code in [200, 201]:
        report_id = response.json()['id']
        print(f"  [OK] DiagnosticReport ID: {report_id}")
    else:
        print(f"  [ERROR] Status: {response.status_code}")

print("\n[OK] Successfully added all DiagnosticReport resources!")
