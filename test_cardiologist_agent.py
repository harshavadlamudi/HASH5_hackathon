import boto3
from dotenv import load_dotenv

load_dotenv()

CARDIOLOGIST_AGENT_ID = 'CDMSLUEUFQ'
REGION = 'us-west-2'

# Sample cardiac data for Sarah Johnson
SAMPLE_CARDIAC_DATA = """
Patient: Sarah Johnson
Patient ID: 6df562fc-25a7-4e72-8753-9583e3259572

CARDIAC DATA:
- Condition: Atrial fibrillation
- ECG: Irregular rhythm, heart rate 85-110 bpm, no ST changes
- Cardiac MRI: Enlarged left atrium (4.5 cm), normal ventricular function
- Blood Pressure: 135/85 mmHg
- Medications: None currently prescribed

Please analyze this cardiac data and provide your assessment.
"""

def test_cardiologist_agent():
    """Test Cardiologist Agent with sample data"""
    
    # First, prepare the agent
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    print("Preparing Cardiologist Agent...")
    try:
        bedrock_agent.prepare_agent(agentId=CARDIOLOGIST_AGENT_ID)
        print("[OK] Agent prepared")
    except Exception as e:
        print(f"[WARN] Prepare failed: {e}")
    
    # Create alias if needed
    print("\nCreating/Getting agent alias...")
    try:
        alias_response = bedrock_agent.create_agent_alias(
            agentId=CARDIOLOGIST_AGENT_ID,
            agentAliasName='CardioAlias'
        )
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"[OK] Alias created: {alias_id}")
    except Exception as e:
        # Try to list existing aliases
        aliases = bedrock_agent.list_agent_aliases(agentId=CARDIOLOGIST_AGENT_ID)
        if aliases['agentAliasSummaries']:
            alias_id = aliases['agentAliasSummaries'][0]['agentAliasId']
            print(f"[OK] Using existing alias: {alias_id}")
        else:
            print(f"[ERROR] No alias found: {e}")
            return
    
    # Test the agent
    print("\n" + "="*50)
    print("TESTING CARDIOLOGIST AGENT")
    print("="*50)
    print("\nSending cardiac data...")
    
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=CARDIOLOGIST_AGENT_ID,
        agentAliasId=alias_id,
        sessionId='test-session-001',
        inputText=SAMPLE_CARDIAC_DATA
    )
    
    print("\nCARDIOLOGIST RESPONSE:")
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
    test_cardiologist_agent()
