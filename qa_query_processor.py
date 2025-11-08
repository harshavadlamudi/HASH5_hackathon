import boto3
import json
import uuid
from report_cache_manager import get_cached_context

REGION = 'us-west-2'

with open('agent_config.json', 'r') as f:
    config = json.load(f)

QA_AGENT_ID = config['qa_agent']['agent_id']
QA_ALIAS_ID = config['qa_agent']['alias_id']

def process_user_query(question, session_state):
    """Process user query and return structured response"""
    context = get_cached_context(session_state)
    
    if not context:
        return {
            'answer': 'No cached reports available. Please generate a comprehensive report first.',
            'ui_type': 'detailed_card',
            'data': {
                'title': 'No Data',
                'summary': 'Generate a comprehensive report to ask questions.',
                'details': [],
                'implications': ''
            }
        }
    
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    prompt = f"""
{context}

USER QUESTION: {question}

Respond in JSON format with: answer, ui_type, data, sources, confidence
"""
    
    response = runtime.invoke_agent(
        agentId=QA_AGENT_ID,
        agentAliasId=QA_ALIAS_ID,
        sessionId=str(uuid.uuid4()),
        inputText=prompt
    )
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
    
    return parse_agent_response(completion, question)

def parse_agent_response(response, question):
    """Parse agent response and extract structured data"""
    try:
        parsed = json.loads(response)
        return parsed
    except:
        # Fallback if agent doesn't return JSON
        return {
            'answer': response,
            'ui_type': 'detailed_card',
            'data': {
                'title': 'Response',
                'summary': response[:200] + '...' if len(response) > 200 else response,
                'details': [response],
                'implications': ''
            },
            'sources': ['comprehensive'],
            'confidence': 'medium'
        }

def add_to_history(session_state, question, response):
    """Add Q&A to conversation history"""
    if 'qa_history' not in session_state:
        session_state['qa_history'] = []
    
    session_state['qa_history'].append({
        'question': question,
        'response': response
    })
