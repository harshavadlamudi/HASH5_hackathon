import boto3
import json
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from PIL import Image, ImageDraw, ImageFont
import io

load_dotenv()

REGION = 'us-west-2'
DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'

# MRI Patient IDs from previous script
MRI_PATIENTS = [
    {"id": "6f0bc274-9b4e-4cc0-80eb-d49aa2f6da9a", "name": "Michael Anderson", "type": "Brain MRI", "label": "Brain Tumor"},
    {"id": "89698d95-8e01-4d88-8f00-945372d5aac9", "name": "Patricia Martinez", "type": "Brain MRI", "label": "Multiple Sclerosis"},
    {"id": "3ac6d9cb-e28f-4322-af37-86704edc03c3", "name": "James Thompson", "type": "Spine MRI", "label": "Disc Herniation"},
    {"id": "db2dca16-3c5f-47e4-98dd-63bcc491e6ac", "name": "Linda Davis", "type": "Knee MRI", "label": "Meniscal Tear"},
    {"id": "a1532ebb-26bf-42c4-a523-ab56d9d76369", "name": "Robert Wilson", "type": "Brain MRI", "label": "Stroke"}
]

def create_sample_mri_image(patient_name, mri_type, label):
    """Generate a sample MRI image"""
    img = Image.new('L', (512, 512), color=20)
    draw = ImageDraw.Draw(img)
    
    # Draw sample MRI-like patterns
    for i in range(0, 512, 32):
        draw.ellipse([128+i//4, 128+i//4, 384-i//4, 384-i//4], outline=100+i//4, width=2)
    
    # Add text
    draw.text((20, 20), f"{mri_type}", fill=255)
    draw.text((20, 480), f"{patient_name} - {label}", fill=255)
    
    # Convert to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

def create_resource(resource):
    """Create FHIR resource in HealthLake"""
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    url = f"{endpoint}{resource['resourceType']}"
    data = json.dumps(resource)
    
    request = AWSRequest(method='POST', url=url, data=data, headers={'Content-Type': 'application/fhir+json'})
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    response = requests.post(url, data=data, headers=dict(request.headers))
    return response

def main():
    print("Adding MRI images to HealthLake patients...\n")
    
    for idx, patient in enumerate(MRI_PATIENTS, 1):
        print(f"[{idx}/5] Adding MRI image for {patient['name']}")
        
        # Generate sample MRI image
        image_data = create_sample_mri_image(patient['name'], patient['type'], patient['label'])
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create Media resource with embedded image
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
                "reference": f"Patient/{patient['id']}",
                "display": patient['name']
            },
            "createdDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content": {
                "contentType": "image/png",
                "data": image_base64,
                "title": f"{patient['type']} - {patient['label']}"
            }
        }
        
        response = create_resource(media_resource)
        
        if response.status_code in [200, 201]:
            media_id = response.json()['id']
            print(f"  [OK] Media ID: {media_id}")
            print(f"  [OK] Image: {patient['type']} - {patient['label']}")
        else:
            print(f"  [ERROR] Status: {response.status_code} - {response.text}")
    
    print("\n[OK] Successfully added MRI images for all patients!")
    print("\nQuery images using:")
    print("  search_healthlake('Media', {'patient': patient_id})")
    print("  Images are base64 encoded in 'content.data' field")

if __name__ == "__main__":
    main()
