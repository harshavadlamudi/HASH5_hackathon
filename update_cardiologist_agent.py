import boto3
import time
from dotenv import load_dotenv

load_dotenv()

CARDIOLOGIST_AGENT_ID = 'CDMSLUEUFQ'
REGION = 'us-west-2'
ROLE_ARN = 'arn:aws:iam::891450252216:role/CardiologistAgentRole'

def update_agent():
    """Update existing Cardiologist Agent with role"""
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    # Read instructions
    with open('cardiologist_agent_instructions.txt', 'r') as f:
        instructions = f.read()
    
    print("Updating Cardiologist Agent...")
    
    try:
        response = bedrock_agent.update_agent(
            agentId=CARDIOLOGIST_AGENT_ID,
            agentName='CardiologistAgent',
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
            instruction=instructions,
            agentResourceRoleArn=ROLE_ARN
        )
        
        print("[OK] Agent updated")
        
        # Prepare agent
        print("Preparing agent...")
        time.sleep(5)
        bedrock_agent.prepare_agent(agentId=CARDIOLOGIST_AGENT_ID)
        print("[OK] Agent prepared")
        
        print("\n" + "="*50)
        print("AGENT READY FOR TESTING!")
        print("="*50)
        print(f"Agent ID: {CARDIOLOGIST_AGENT_ID}")
        print(f"Role ARN: {ROLE_ARN}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    update_agent()
