import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from dotenv import load_dotenv

load_dotenv()

DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'
REGION = 'us-west-2'

def get_all_patients():
    """Fetch all patient names and IDs from HealthLake"""
    return get_all_patient_names()

def get_all_patient_names():
    """Fetch all patient names and IDs from HealthLake"""
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    url = f"{endpoint}Patient?_count=100"
    request = AWSRequest(method='GET', url=url)
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    try:
        response = requests.get(url, headers=dict(request.headers))
        response.raise_for_status()
        data = response.json()
        
        patient_map = {}
        for entry in data.get('entry', []):
            patient = entry['resource']
            patient_id = patient.get('id')
            names = patient.get('name', [])
            
            for name in names:
                given = ' '.join(name.get('given', []))
                family = name.get('family', '')
                full_name = f"{given} {family}".strip()
                
                if full_name and patient_id:
                    patient_map[full_name] = patient_id
        
        return patient_map
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

if __name__ == "__main__":
    patient_map = get_all_patient_names()
    print(f"Found {len(patient_map)} patients:")
    for name, patient_id in list(patient_map.items())[:10]:
        print(f"  - {name} (ID: {patient_id})")
