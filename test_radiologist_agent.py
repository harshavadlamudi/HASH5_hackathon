import boto3
import json
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

# Load config
with open('agent_config.json', 'r') as f:
    config = json.load(f)

RADIOLOGIST_AGENT_ID = config['radiologist_agent']['agent_id']
RADIOLOGIST_ALIAS_ID = config['radiologist_agent']['alias_id']

# Sample MRI data for Sarah Johnson
SAMPLE_MRI_DATA = """
Patient: Sarah Johnson
Patient ID: 6df562fc-25a7-4e72-8753-9583e3259572

IMAGING DATA:
- Modality: Cardiac MRI
- Study Date: 2025-01-31
- Body Part: Heart/Cardiac
- Indication: Atrial fibrillation evaluation

FINDINGS:
- Enlarged left atrium measuring 4.5 cm in diameter
- Normal left ventricular size and function
- Normal right ventricular size and function
- No pericardial effusion
- No valvular abnormalities detected
- Image quality: Excellent

IMPRESSION:
Enlarged left atrium consistent with atrial fibrillation. Normal ventricular function.

Please analyze this imaging data and provide your radiology assessment.
"""

def test_radiologist_agent():
    """Test Radiologist Agent with sample MRI data"""
    
    print("="*50)
    print("TESTING RADIOLOGIST AGENT")
    print("="*50)
    print(f"\nAgent ID: {RADIOLOGIST_AGENT_ID}")
    print(f"Alias ID: {RADIOLOGIST_ALIAS_ID}")
    print("\nSending MRI data...")
    
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=RADIOLOGIST_AGENT_ID,
        agentAliasId=RADIOLOGIST_ALIAS_ID,
        sessionId='test-radio-001',
        inputText=SAMPLE_MRI_DATA
    )
    
    print("\nRADIOLOGIST RESPONSE:")
    print("-" * 50)
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                text = chunk['bytes'].decode('utf-8')
                completion += text
                print(text, end='', flush=True)
    
    print("\n" + "="*50)
    print("TEST COMPLETED!")
    print("="*50)
    
    return completion

if __name__ == "__main__":
    test_radiologist_agent()
