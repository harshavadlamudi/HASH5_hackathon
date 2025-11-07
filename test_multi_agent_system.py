import boto3
import json
from dotenv import load_dotenv

load_dotenv()

REGION = 'us-west-2'

# Load all agent IDs
with open('agent_config.json', 'r') as f:
    config = json.load(f)

def invoke_specialist(agent_id, alias_id, data, session_id):
    """Invoke a specialist agent"""
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=alias_id,
        sessionId=session_id,
        inputText=data
    )
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
    
    return completion

def test_multi_agent_system():
    """Test complete multi-agent system with Sarah Johnson"""
    
    print("="*60)
    print("MULTI-AGENT MEDICAL ANALYSIS SYSTEM TEST")
    print("="*60)
    print("\nPatient: Sarah Johnson")
    print("Patient ID: 6df562fc-25a7-4e72-8753-9583e3259572")
    print("\n" + "-"*60)
    
    # Step 1: Cardiologist Analysis
    print("\n[1/4] Invoking Cardiologist Agent...")
    cardiac_data = """
Patient: Sarah Johnson
Condition: Atrial fibrillation
ECG: Irregular rhythm, HR 85-110 bpm
Cardiac MRI: Enlarged left atrium (4.5 cm)
BP: 135/85 mmHg
Medications: None
"""
    
    cardio_report = invoke_specialist(
        config['cardiologist_agent']['agent_id'],
        config['cardiologist_agent']['alias_id'],
        cardiac_data,
        'test-multi-cardio'
    )
    print("[OK] Cardiology report received")
    
    # Step 2: Radiologist Analysis
    print("\n[2/4] Invoking Radiologist Agent...")
    imaging_data = """
Patient: Sarah Johnson
Modality: Cardiac MRI
Findings: Enlarged left atrium (4.5 cm), normal ventricular function
Quality: Excellent
"""
    
    radio_report = invoke_specialist(
        config['radiologist_agent']['agent_id'],
        config['radiologist_agent']['alias_id'],
        imaging_data,
        'test-multi-radio'
    )
    print("[OK] Radiology report received")
    
    # Step 3: Endocrinologist Analysis
    print("\n[3/4] Invoking Endocrinologist Agent...")
    metabolic_data = """
Patient: Sarah Johnson
Labs: Glucose 95 mg/dL, HbA1c 5.4%, TSH 2.1 mIU/L
Lipids: Total 185, LDL 110, HDL 55, TG 100 mg/dL
BMI: 24.5
"""
    
    endo_report = invoke_specialist(
        config['endocrinologist_agent']['agent_id'],
        config['endocrinologist_agent']['alias_id'],
        metabolic_data,
        'test-multi-endo'
    )
    print("[OK] Endocrinology report received")
    
    # Step 4: Orchestrator - Combine all reports
    print("\n[4/4] Invoking Orchestrator Agent...")
    combined_input = f"""
Patient: Sarah Johnson (ID: 6df562fc-25a7-4e72-8753-9583e3259572)

CARDIOLOGY: Atrial fibrillation, enlarged left atrium, moderate risk
RADIOLOGY: Cardiac MRI shows 4.5cm left atrial enlargement
ENDOCRINOLOGY: Normal metabolic panel, borderline LDL cholesterol

Generate comprehensive report.
"""
    
    final_report = invoke_specialist(
        config['orchestrator_agent']['agent_id'],
        config['orchestrator_agent']['alias_id'],
        combined_input,
        'test-multi-orchestrator'
    )
    
    print("\n" + "="*60)
    print("COMPREHENSIVE MEDICAL REPORT")
    print("="*60)
    print(final_report)
    print("\n" + "="*60)
    print("MULTI-AGENT SYSTEM TEST COMPLETED!")
    print("="*60)
    
    return final_report

if __name__ == "__main__":
    test_multi_agent_system()
