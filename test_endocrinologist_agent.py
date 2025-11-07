import boto3
import json
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

# Load config
with open('agent_config.json', 'r') as f:
    config = json.load(f)

ENDO_AGENT_ID = config['endocrinologist_agent']['agent_id']
ENDO_ALIAS_ID = config['endocrinologist_agent']['alias_id']

# Sample metabolic data
SAMPLE_METABOLIC_DATA = """
Patient: Sarah Johnson
Patient ID: 6df562fc-25a7-4e72-8753-9583e3259572

LABORATORY RESULTS:
- Glucose (fasting): 95 mg/dL (normal: 70-100 mg/dL)
- HbA1c: 5.4% (normal: <5.7%)
- TSH: 2.1 mIU/L (normal: 0.4-4.0 mIU/L)
- Total Cholesterol: 185 mg/dL (desirable: <200 mg/dL)
- LDL: 110 mg/dL (optimal: <100 mg/dL)
- HDL: 55 mg/dL (normal: >40 mg/dL)
- Triglycerides: 100 mg/dL (normal: <150 mg/dL)

VITAL SIGNS:
- BMI: 24.5 (normal weight)
- Blood Pressure: 135/85 mmHg

MEDICATIONS:
- None for metabolic/endocrine conditions

MEDICAL HISTORY:
- No diabetes
- No thyroid disease
- Atrial fibrillation (cardiac condition)

Please analyze this metabolic and endocrine data.
"""

def test_endocrinologist_agent():
    """Test Endocrinologist Agent"""
    
    print("="*50)
    print("TESTING ENDOCRINOLOGIST AGENT")
    print("="*50)
    print(f"\nAgent ID: {ENDO_AGENT_ID}")
    print(f"Alias ID: {ENDO_ALIAS_ID}")
    print("\nSending metabolic data...")
    
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=ENDO_AGENT_ID,
        agentAliasId=ENDO_ALIAS_ID,
        sessionId='test-endo-001',
        inputText=SAMPLE_METABOLIC_DATA
    )
    
    print("\nENDOCRINOLOGIST RESPONSE:")
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
    test_endocrinologist_agent()
