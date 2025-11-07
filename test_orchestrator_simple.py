import boto3
import json
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

with open('agent_config.json', 'r') as f:
    config = json.load(f)

ORCHESTRATOR_ID = config['orchestrator_agent']['agent_id']
ORCHESTRATOR_ALIAS = config['orchestrator_agent']['alias_id']

# Simple test input
test_input = """
Patient: Sarah Johnson
Patient ID: 6df562fc-25a7-4e72-8753-9583e3259572

SPECIALIST REPORTS SUMMARY:

CARDIOLOGY:
- Finding: Atrial fibrillation with irregular rhythm
- Risk: Moderate cardiovascular risk
- Recommendation: Anticoagulation therapy needed

RADIOLOGY:
- Finding: Enlarged left atrium (4.5 cm) on cardiac MRI
- Severity: Moderate
- Recommendation: Follow-up MRI in 6-12 months

ENDOCRINOLOGY:
- Finding: Borderline high LDL cholesterol (110 mg/dL)
- Risk: Moderate cardiovascular risk
- Recommendation: Lifestyle modifications

Please generate a comprehensive integrated medical report.
"""

def test_orchestrator():
    print("Testing Orchestrator Agent...")
    print("="*50)
    
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=ORCHESTRATOR_ID,
        agentAliasId=ORCHESTRATOR_ALIAS,
        sessionId='test-orch-simple',
        inputText=test_input
    )
    
    print("\nORCHESTRATOR RESPONSE:")
    print("-"*50)
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                text = chunk['bytes'].decode('utf-8')
                completion += text
                print(text, end='', flush=True)
    
    print("\n" + "="*50)
    return completion

if __name__ == "__main__":
    test_orchestrator()
