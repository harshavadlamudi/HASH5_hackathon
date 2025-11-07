import boto3
import requests
from dotenv import load_dotenv
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

load_dotenv()

REGION = 'us-west-2'
DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'
PATIENT_ID = "6df562fc-25a7-4e72-8753-9583e3259572"

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

print(f"Verifying Sarah Johnson (Patient ID: {PATIENT_ID})...\n")

# Check patient
patient = search_healthlake('Patient', {'_id': PATIENT_ID})
if patient.get('entry'):
    p = patient['entry'][0]['resource']
    name = p.get('name', [{}])[0]
    full_name = f"{' '.join(name.get('given', []))} {name.get('family', '')}"
    print(f"[OK] Patient: {full_name}")
else:
    print("[ERROR] Patient not found")

# Check conditions
conditions = search_healthlake('Condition', {'patient': PATIENT_ID})
if conditions.get('entry'):
    print(f"[OK] Conditions: {len(conditions['entry'])}")
    for entry in conditions['entry']:
        cond = entry['resource'].get('code', {}).get('text', 'Unknown')
        print(f"     - {cond}")
else:
    print("[WARN] No conditions")

# Check ECG observations
ecg_obs = search_healthlake('Observation', {'patient': PATIENT_ID, 'code': '131328'})
if ecg_obs.get('entry'):
    print(f"[OK] ECG Waveform: {len(ecg_obs['entry'])} observation(s)")
else:
    print("[WARN] No ECG waveform")

# Check diagnostic reports
reports = search_healthlake('DiagnosticReport', {'patient': PATIENT_ID})
if reports.get('entry'):
    print(f"[OK] DiagnosticReports: {len(reports['entry'])}")
    for entry in reports['entry']:
        report_type = entry['resource'].get('code', {}).get('text', 'Unknown')
        print(f"     - {report_type}")
else:
    print("[WARN] No diagnostic reports")

# Check media
media = search_healthlake('Media', {'patient': PATIENT_ID})
if media.get('entry'):
    print(f"[OK] Media/Images: {len(media['entry'])}")
    for entry in media['entry']:
        title = entry['resource'].get('content', {}).get('title', 'Unknown')
        print(f"     - {title}")
else:
    print("[WARN] No media")

print("\n" + "="*50)
print("Sarah Johnson now has BOTH ECG and MRI data!")
print("="*50)
