import boto3
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

with open('agent_config.json', 'r') as f:
    config = json.load(f)

AGENT_ID = config['qa_agent']['agent_id']
ALIAS_ID = config['qa_agent']['alias_id']

def invoke_qa_agent(question, cached_reports):
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    prompt = f"""
CACHED REPORTS:
{json.dumps(cached_reports, indent=2)}

USER QUESTION: {question}
"""
    
    response = runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        sessionId=str(uuid.uuid4()),
        inputText=prompt
    )
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
    
    return completion

# Sample cached reports
sample_reports = {
    "patient": {
        "name": "Sarah Johnson",
        "id": "12345",
        "age": 45,
        "gender": "Female"
    },
    "cardiology": """
    CARDIOLOGY ANALYSIS:
    - Diagnosis: Atrial Fibrillation (AFib)
    - ECG Findings: Irregular rhythm, no P waves
    - Risk Assessment: Moderate stroke risk
    - Recommendations: Start anticoagulation, cardiology follow-up in 2 weeks
    """,
    "radiology": """
    RADIOLOGY ANALYSIS:
    - Cardiac MRI: Enlarged left atrium (4.5cm diameter)
    - Findings: Above normal range, consistent with AFib
    - Recommendations: Monitor for progression, repeat imaging in 6 months
    """,
    "endocrinology": """
    ENDOCRINOLOGY ANALYSIS:
    - LDL Cholesterol: 145 mg/dL (borderline high)
    - Glucose: Normal
    - Recommendations: Consider statin therapy, lifestyle modifications
    """,
    "comprehensive": """
    COMPREHENSIVE SUMMARY:
    Patient has atrial fibrillation with enlarged left atrium and borderline high cholesterol.
    Priority actions: 1) Anticoagulation 2) Cardiology follow-up 3) Cholesterol management
    Overall risk: Moderate cardiovascular risk requiring active management
    """
}

if __name__ == '__main__':
    print("Testing Medical Q&A Agent\n")
    
    test_questions = [
        "What are my top health risks?",
        "What should I do first?",
        "Compare what the cardiologist and radiologist found",
        "What follow-up appointments do I need?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {question}")
        print('='*60)
        
        response = invoke_qa_agent(question, sample_reports)
        print(response)
        
        try:
            parsed = json.loads(response)
            print(f"\n[OK] Valid JSON response")
            print(f"UI Type: {parsed.get('ui_type')}")
            print(f"Sources: {parsed.get('sources')}")
        except:
            print("\n[WARN] Response is not valid JSON - agent needs instruction refinement")
