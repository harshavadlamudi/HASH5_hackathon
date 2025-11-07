import boto3
import json
import time
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

def create_agent_role():
    """Create IAM role for Radiologist Agent"""
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
            RoleName='RadiologistAgentRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Radiologist Bedrock Agent'
        )
        role_arn = response['Role']['Arn']
        print(f"[OK] IAM Role created: {role_arn}")
        
        iam.attach_role_policy(
            RoleName='RadiologistAgentRole',
            PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
        )
        print("[OK] Policy attached")
        
        time.sleep(10)
        return role_arn
        
    except iam.exceptions.EntityAlreadyExistsException:
        response = iam.get_role(RoleName='RadiologistAgentRole')
        role_arn = response['Role']['Arn']
        print(f"[OK] Using existing role: {role_arn}")
        return role_arn

def create_radiologist_agent():
    """Create Radiologist Bedrock Agent"""
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    with open('radiologist_agent_instructions.txt', 'r') as f:
        instructions = f.read()
    
    print("Creating Radiologist Agent...")
    
    try:
        role_arn = create_agent_role()
        
        response = bedrock_agent.create_agent(
            agentName='RadiologistAgent',
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
            instruction=instructions,
            agentResourceRoleArn=role_arn,
            description='Specialized radiologist agent for medical imaging analysis'
        )
        
        agent_id = response['agent']['agentId']
        print(f"[OK] Agent created: {agent_id}")
        
        print("Preparing agent...")
        time.sleep(5)
        bedrock_agent.prepare_agent(agentId=agent_id)
        print("[OK] Agent prepared")
        
        print("Creating agent alias...")
        alias_response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName='RadioAlias'
        )
        
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"[OK] Alias created: {alias_id}")
        
        # Update config file
        with open('agent_config.json', 'r') as f:
            config = json.load(f)
        
        config['radiologist_agent']['agent_id'] = agent_id
        config['radiologist_agent']['alias_id'] = alias_id
        
        with open('agent_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("[OK] Config file updated")
        
        print("\n" + "="*50)
        print("RADIOLOGIST AGENT DEPLOYED SUCCESSFULLY!")
        print("="*50)
        print(f"Agent ID: {agent_id}")
        print(f"Alias ID: {alias_id}")
        
        return agent_id, alias_id
        
    except Exception as e:
        print(f"[ERROR] Failed: {str(e)}")
        return None, None

if __name__ == "__main__":
    create_radiologist_agent()
