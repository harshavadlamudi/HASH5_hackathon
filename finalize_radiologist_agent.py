import boto3
import json
import time
from dotenv import load_dotenv

load_dotenv()

RADIOLOGIST_AGENT_ID = 'K0MU8VCNSK'
REGION = 'us-west-2'

def finalize_agent():
    """Create alias for Radiologist Agent"""
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    print("Waiting for agent to be ready...")
    time.sleep(15)
    
    print("Creating agent alias...")
    try:
        alias_response = bedrock_agent.create_agent_alias(
            agentId=RADIOLOGIST_AGENT_ID,
            agentAliasName='RadioAlias'
        )
        
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"[OK] Alias created: {alias_id}")
        
        # Update config file
        with open('agent_config.json', 'r') as f:
            config = json.load(f)
        
        config['radiologist_agent']['agent_id'] = RADIOLOGIST_AGENT_ID
        config['radiologist_agent']['alias_id'] = alias_id
        
        with open('agent_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("[OK] Config file updated")
        
        print("\n" + "="*50)
        print("RADIOLOGIST AGENT READY!")
        print("="*50)
        print(f"Agent ID: {RADIOLOGIST_AGENT_ID}")
        print(f"Alias ID: {alias_id}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    finalize_agent()
