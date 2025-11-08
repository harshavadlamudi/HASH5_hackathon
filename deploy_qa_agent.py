import boto3
import json
import time
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'
AGENT_NAME = 'MedicalQAAgent'
MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'

def create_agent_role():
    iam = boto3.client('iam', region_name=REGION)
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    role_name = f'{AGENT_NAME}Role'
    
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Medical Q&A Agent'
        )
        role_arn = response['Role']['Arn']
        print(f"Created role: {role_arn}")
        
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
        )
        print("Attached Bedrock policy")
        
        time.sleep(10)
        return role_arn
        
    except iam.exceptions.EntityAlreadyExistsException:
        response = iam.get_role(RoleName=role_name)
        print(f"Role already exists: {response['Role']['Arn']}")
        return response['Role']['Arn']

def create_qa_agent(role_arn):
    bedrock = boto3.client('bedrock-agent', region_name=REGION)
    
    with open('qa_agent_instructions.txt', 'r') as f:
        instructions = f.read()
    
    response = bedrock.create_agent(
        agentName=AGENT_NAME,
        agentResourceRoleArn=role_arn,
        foundationModel=MODEL_ID,
        instruction=instructions,
        description='Medical Q&A agent for answering questions about cached analysis reports'
    )
    
    agent_id = response['agent']['agentId']
    print(f"Created agent: {agent_id}")
    
    time.sleep(15)
    
    bedrock.prepare_agent(agentId=agent_id)
    print("Preparing agent...")
    time.sleep(20)
    
    alias_response = bedrock.create_agent_alias(
        agentId=agent_id,
        agentAliasName='prod',
        description='Production alias for Q&A agent'
    )
    
    alias_id = alias_response['agentAlias']['agentAliasId']
    print(f"Created alias: {alias_id}")
    
    return agent_id, alias_id

def update_agent_config(agent_id, alias_id):
    with open('agent_config.json', 'r') as f:
        config = json.load(f)
    
    config['qa_agent'] = {
        'agent_id': agent_id,
        'alias_id': alias_id
    }
    
    with open('agent_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Updated agent_config.json")

if __name__ == '__main__':
    print("Deploying Medical Q&A Agent...")
    
    role_arn = create_agent_role()
    agent_id, alias_id = create_qa_agent(role_arn)
    update_agent_config(agent_id, alias_id)
    
    print("\n=== Deployment Complete ===")
    print(f"Agent ID: {agent_id}")
    print(f"Alias ID: {alias_id}")
    print("\nRun test_qa_agent.py to test the agent")
