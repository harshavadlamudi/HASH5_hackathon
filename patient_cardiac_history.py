import boto3
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'
REGION = 'us-west-2'

def search_healthlake(resource_type, params=None):
    """Search HealthLake"""
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    url = f"{endpoint}{resource_type}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    request = AWSRequest(method='GET', url=url)
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    response = requests.get(url, headers=dict(request.headers))
    return response.json()

def get_patient_cardiac_history(patient_id):
    """Get complete cardiac history for a patient"""
    
    print("=" * 80)
    print("PATIENT CARDIAC HISTORY REPORT")
    print("=" * 80)
    
    # 1. Get Patient Demographics
    print("\n1. PATIENT INFORMATION")
    print("-" * 80)
    patient_data = search_healthlake('Patient', {'_id': patient_id})
    
    if not patient_data.get('entry'):
        print(f"Patient {patient_id} not found")
        return None
    
    patient = patient_data['entry'][0]['resource']
    name = patient.get('name', [{}])[0]
    full_name = f"{name.get('given', [''])[0]} {name.get('family', '')}"
    
    print(f"Name: {full_name}")
    print(f"Gender: {patient.get('gender', 'Unknown')}")
    print(f"Birth Date: {patient.get('birthDate', 'Unknown')}")
    print(f"Patient ID: {patient_id}")
    
    # 2. Get Cardiac Conditions
    print("\n2. CARDIAC CONDITIONS")
    print("-" * 80)
    conditions = search_healthlake('Condition', {'patient': patient_id, '_count': '50'})
    
    condition_list = []
    if conditions.get('entry'):
        for entry in conditions['entry']:
            cond = entry['resource']
            code = cond.get('code', {}).get('coding', [{}])[0]
            condition_name = code.get('display', 'Unknown')
            status = cond.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', 'unknown')
            onset = cond.get('onsetDateTime', 'Unknown')
            
            print(f"  - {condition_name}")
            print(f"    Status: {status}")
            print(f"    Onset: {onset}")
            condition_list.append(condition_name)
    else:
        print("  No conditions found")
    
    # 3. Get ECG Observations (measurements)
    print("\n3. ECG MEASUREMENTS")
    print("-" * 80)
    ecg_obs = search_healthlake('Observation', {'patient': patient_id, 'code': '11524-6', '_count': '50'})
    
    if ecg_obs.get('entry'):
        for entry in ecg_obs['entry']:
            obs = entry['resource']
            date = obs.get('effectiveDateTime', 'Unknown')
            print(f"\n  ECG Date: {date}")
            
            if 'component' in obs:
                for comp in obs['component']:
                    comp_code = comp.get('code', {}).get('coding', [{}])[0]
                    comp_name = comp_code.get('display', 'Unknown')
                    value = comp.get('valueQuantity', {})
                    print(f"    {comp_name}: {value.get('value')} {value.get('unit', '')}")
    else:
        print("  No ECG measurements found")
    
    # 4. Get ECG Waveforms
    print("\n4. ECG WAVEFORM DATA")
    print("-" * 80)
    waveform_obs = search_healthlake('Observation', {'patient': patient_id, 'code': '131328', '_count': '50'})
    
    waveform_data = None
    if waveform_obs.get('entry'):
        obs = waveform_obs['entry'][0]['resource']
        if 'valueSampledData' in obs:
            sampled_data = obs['valueSampledData']
            data_string = sampled_data['data']
            period_ms = sampled_data['period']
            
            waveform = [float(x) for x in data_string.split()]
            time = np.arange(len(waveform)) * period_ms / 1000
            
            waveform_data = {'time': time, 'amplitude': waveform, 'patient': full_name}
            print(f"  Waveform available: {len(waveform)} samples over {max(time):.1f} seconds")
        else:
            print("  No waveform data found")
    else:
        print("  No waveform observations found")
    
    # 5. Get Diagnostic Reports
    print("\n5. DIAGNOSTIC REPORTS")
    print("-" * 80)
    reports = search_healthlake('DiagnosticReport', {'patient': patient_id, '_count': '50'})
    
    if reports.get('entry'):
        for entry in reports['entry']:
            report = entry['resource']
            code = report.get('code', {}).get('coding', [{}])[0]
            report_name = code.get('display', 'Unknown')
            date = report.get('effectiveDateTime', 'Unknown')
            conclusion = report.get('conclusion', 'No conclusion')
            
            print(f"\n  Report: {report_name}")
            print(f"  Date: {date}")
            print(f"  Conclusion: {conclusion}")
    else:
        print("  No diagnostic reports found")
    
    return {
        'patient': full_name,
        'patient_id': patient_id,
        'conditions': condition_list,
        'waveform': waveform_data
    }

def visualize_patient_ecg(history_data):
    """Visualize patient ECG waveform"""
    
    if not history_data or not history_data.get('waveform'):
        print("\nNo waveform data to visualize")
        return
    
    waveform = history_data['waveform']
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(waveform['time'], waveform['amplitude'], 'b-', linewidth=1.2)
    ax.set_title(f"ECG Lead II - {waveform['patient']}\nConditions: {', '.join(history_data['conditions'])}", 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Amplitude (mV)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim([0, max(waveform['time'])])
    
    # Add annotations
    ax.axhline(y=0, color='r', linestyle='-', linewidth=0.5, alpha=0.5)
    
    plt.tight_layout()
    filename = f"patient_{history_data['patient_id']}_ecg.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n[OK] ECG visualization saved to: {filename}")
    plt.show()

if __name__ == "__main__":
    # Example: Use one of the cardiac patient IDs
    PATIENT_IDS = {
        "Sarah Johnson (AFib)": "6df562fc-25a7-4e72-8753-9583e3259572",
        "Robert Williams (MI)": "02ddeba7-45bc-4a90-962f-6044be99005a",
        "Maria Garcia (Heart Failure)": "c629b0db-4204-4cad-a9bd-7d13efdf6594",
        "David Chen (VTach)": "1923687c-0068-47bd-96a9-8ef34801dc9c",
        "Jennifer Brown (CAD)": "b9b10962-05fe-4912-944e-21a6ff2ae2b2",
    }
    
    print("Available Cardiac Patients:")
    for i, (name, pid) in enumerate(PATIENT_IDS.items(), 1):
        print(f"{i}. {name}")
    
    # Select patient (change this to query different patients)
    selected_patient = "6df562fc-25a7-4e72-8753-9583e3259572"  # Sarah Johnson
    
    print(f"\nGenerating history for patient: {selected_patient}\n")
    
    # Get complete history
    history = get_patient_cardiac_history(selected_patient)
    
    # Visualize ECG
    if history:
        print("\n" + "=" * 80)
        print("GENERATING ECG VISUALIZATION")
        print("=" * 80)
        visualize_patient_ecg(history)
        
        print("\n" + "=" * 80)
        print("REPORT COMPLETE")
        print("=" * 80)
