import boto3
import json
import time
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

def create_agent_role():
    """Create IAM role for Cardiologist Agent"""
    iam = boto3.client('iam')
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        response = iam.create_role(
            RoleName='CardiologistAgentRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Cardiologist Bedrock Agent'
        )
        role_arn = response['Role']['Arn']
        print(f"[OK] IAM Role created: {role_arn}")
        
        # Attach basic Bedrock policy
        iam.attach_role_policy(
            RoleName='CardiologistAgentRole',
            PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
        )
        print("[OK] Policy attached")
        
        time.sleep(10)  # Wait for role to propagate
        return role_arn
        
    except iam.exceptions.EntityAlreadyExistsException:
        response = iam.get_role(RoleName='CardiologistAgentRole')
        role_arn = response['Role']['Arn']
        print(f"[OK] Using existing role: {role_arn}")
        return role_arn

def create_cardiologist_agent():
    """Create Cardiologist Bedrock Agent"""
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    # Read instructions
    with open('cardiologist_agent_instructions.txt', 'r') as f:
        instructions = f.read()
    
    print("Creating Cardiologist Agent...")
    
    try:
        # Create IAM role
        role_arn = create_agent_role()
        
        # Create agent
        response = bedrock_agent.create_agent(
            agentName='CardiologistAgent',
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
            instruction=instructions,
            agentResourceRoleArn=role_arn,
            description='Specialized cardiologist agent for cardiac data analysis'
        )
        
        agent_id = response['agent']['agentId']
        print(f"[OK] Agent created: {agent_id}")
        
        # Prepare agent
        print("Preparing agent...")
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("[OK] Agent prepared")
        
        # Create alias
        print("Creating agent alias...")
        alias_response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName='CardioAlias'
        )
        
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"[OK] Alias created: {alias_id}")
        
        print("\n" + "="*50)
        print("CARDIOLOGIST AGENT DEPLOYED SUCCESSFULLY!")
        print("="*50)
        print(f"Agent ID: {agent_id}")
        print(f"Alias ID: {alias_id}")
        print("\nSave these IDs for testing!")
        
        return agent_id, alias_id
        
    except Exception as e:
        print(f"[ERROR] Failed to create agent: {str(e)}")
        return None, None

if __name__ == "__main__":
    create_cardiologist_agent()
