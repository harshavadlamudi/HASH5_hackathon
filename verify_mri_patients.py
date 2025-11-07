import boto3
import requests
from dotenv import load_dotenv
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

load_dotenv()

REGION = 'us-west-2'
DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'

def search_healthlake(resource_type, params=None):
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    url = f"{endpoint}{resource_type}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    request = AWSRequest(method='GET', url=url)
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    response = requests.get(url, headers=dict(request.headers))
    return response.json()

# Check MRI patients
mri_patient_ids = [
    "6f0bc274-9b4e-4cc0-80eb-d49aa2f6da9a",
    "89698d95-8e01-4d88-8f00-945372d5aac9",
    "3ac6d9cb-e28f-4322-af37-86704edc03c3",
    "db2dca16-3c5f-47e4-98dd-63bcc491e6ac",
    "a1532ebb-26bf-42c4-a523-ab56d9d76369"
]

print("Verifying MRI patients in HealthLake...\n")

for patient_id in mri_patient_ids:
    print(f"Patient ID: {patient_id}")
    
    # Check patient
    patient = search_healthlake('Patient', {'_id': patient_id})
    if patient.get('entry'):
        p = patient['entry'][0]['resource']
        name = p.get('name', [{}])[0]
        full_name = f"{' '.join(name.get('given', []))} {name.get('family', '')}"
        print(f"  [OK] Patient: {full_name}")
    else:
        print(f"  [ERROR] Patient not found")
        continue
    
    # Check conditions
    conditions = search_healthlake('Condition', {'patient': patient_id})
    if conditions.get('entry'):
        print(f"  [OK] Conditions: {len(conditions['entry'])}")
    else:
        print(f"  [WARN] No conditions")
    
    # Check diagnostic reports
    reports = search_healthlake('DiagnosticReport', {'patient': patient_id})
    if reports.get('entry'):
        print(f"  [OK] DiagnosticReports: {len(reports['entry'])}")
    else:
        print(f"  [WARN] No diagnostic reports")
    
    # Check media
    media = search_healthlake('Media', {'patient': patient_id})
    if media.get('entry'):
        print(f"  [OK] Media: {len(media['entry'])}")
    else:
        print(f"  [WARN] No media")
    
    print()
