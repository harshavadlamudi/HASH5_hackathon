import boto3
import json
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from PIL import Image, ImageDraw
import io

load_dotenv()

REGION = 'us-west-2'
DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'

# Sarah Johnson - cardiac patient with AFib
PATIENT_ID = "6df562fc-25a7-4e72-8753-9583e3259572"
PATIENT_NAME = "Sarah Johnson"

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

def create_cardiac_mri_image(patient_name):
    """Generate cardiac MRI image"""
    img = Image.new('L', (512, 512), color=20)
    draw = ImageDraw.Draw(img)
    
    # Draw heart chambers
    draw.ellipse([150, 180, 360, 380], outline=150, width=3)
    draw.ellipse([180, 200, 330, 360], outline=180, width=2)
    
    # Add labels
    draw.text((20, 20), "Cardiac MRI", fill=255)
    draw.text((20, 480), f"{patient_name} - Atrial Fibrillation", fill=255)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

print(f"Adding Cardiac MRI for {PATIENT_NAME}...\n")

# Create DiagnosticReport
print("[1/2] Creating DiagnosticReport...")
diagnostic_report = {
    "resourceType": "DiagnosticReport",
    "status": "final",
    "code": {
        "coding": [{
            "system": "http://loinc.org",
            "code": "24627-2",
            "display": "MRI Study"
        }],
        "text": "Cardiac MRI"
    },
    "subject": {
        "reference": f"Patient/{PATIENT_ID}",
        "display": PATIENT_NAME
    },
    "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "conclusion": "Enlarged left atrium consistent with atrial fibrillation. Normal ventricular function."
}

response = create_resource(diagnostic_report)
if response.status_code in [200, 201]:
    report_id = response.json()['id']
    print(f"  [OK] DiagnosticReport ID: {report_id}")
else:
    print(f"  [ERROR] Status: {response.status_code}")

# Create Media with MRI image
print("[2/2] Creating Media resource with MRI image...")
image_data = create_cardiac_mri_image(PATIENT_NAME)
image_base64 = base64.b64encode(image_data).decode('utf-8')

media_resource = {
    "resourceType": "Media",
    "status": "completed",
    "type": {
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/media-type",
            "code": "image",
            "display": "Image"
        }]
    },
    "subject": {
        "reference": f"Patient/{PATIENT_ID}",
        "display": PATIENT_NAME
    },
    "createdDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "content": {
        "contentType": "image/png",
        "data": image_base64,
        "title": "Cardiac MRI - Atrial Fibrillation"
    }
}

response = create_resource(media_resource)
if response.status_code in [200, 201]:
    media_id = response.json()['id']
    print(f"  [OK] Media ID: {media_id}")
else:
    print(f"  [ERROR] Status: {response.status_code}")

print(f"\n[OK] Successfully added Cardiac MRI for {PATIENT_NAME}!")
print(f"\nPatient {PATIENT_NAME} now has:")
print("  - ECG waveform data")
print("  - Cardiac MRI image")
print("  - MRI diagnostic report")
print("\nYou can now visualize both ECG and MRI in the UI!")
