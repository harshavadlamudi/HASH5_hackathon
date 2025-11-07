import boto3
import json
import requests
import numpy as np
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'
REGION = 'us-west-2'

def post_to_healthlake(resource):
    """Post FHIR resource to HealthLake"""
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    
    resource_type = resource['resourceType']
    url = f"{endpoint}{resource_type}"
    
    request = AWSRequest(method='POST', url=url, data=json.dumps(resource), 
                        headers={'Content-Type': 'application/fhir+json'})
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    response = requests.post(url, data=json.dumps(resource), headers=dict(request.headers))
    response.raise_for_status()
    return response.json()

def generate_ecg_waveform(condition_type, duration_seconds=10, sampling_rate=500):
    """Generate synthetic ECG waveform data"""
    num_samples = duration_seconds * sampling_rate
    time = np.linspace(0, duration_seconds, num_samples)
    
    # Base parameters
    heart_rate = 75  # beats per minute
    
    if condition_type == "normal":
        heart_rate = 72
        amplitude = 1.0
        noise = 0.05
    elif condition_type == "afib":
        heart_rate = 110
        amplitude = 0.8
        noise = 0.15  # More irregular
    elif condition_type == "mi":
        heart_rate = 95
        amplitude = 1.2
        noise = 0.08
    elif condition_type == "vtach":
        heart_rate = 145
        amplitude = 1.5
        noise = 0.1
    else:
        heart_rate = 75
        amplitude = 1.0
        noise = 0.05
    
    # Generate ECG-like waveform
    beat_duration = 60.0 / heart_rate
    ecg_signal = np.zeros(num_samples)
    
    for i in range(num_samples):
        t = time[i] % beat_duration
        
        # P wave (atrial depolarization)
        if 0 <= t < 0.1:
            ecg_signal[i] = amplitude * 0.2 * np.sin(np.pi * t / 0.1)
        
        # PR segment
        elif 0.1 <= t < 0.16:
            ecg_signal[i] = 0
        
        # QRS complex (ventricular depolarization)
        elif 0.16 <= t < 0.18:
            ecg_signal[i] = -amplitude * 0.3
        elif 0.18 <= t < 0.22:
            ecg_signal[i] = amplitude * 1.5 * np.sin(np.pi * (t - 0.18) / 0.04)
        elif 0.22 <= t < 0.24:
            ecg_signal[i] = -amplitude * 0.2
        
        # ST segment
        elif 0.24 <= t < 0.32:
            ecg_signal[i] = 0
        
        # T wave (ventricular repolarization)
        elif 0.32 <= t < 0.48:
            ecg_signal[i] = amplitude * 0.3 * np.sin(np.pi * (t - 0.32) / 0.16)
        
        # Add noise
        ecg_signal[i] += np.random.normal(0, noise * amplitude)
    
    # For AFib, remove P waves and make irregular
    if condition_type == "afib":
        ecg_signal = ecg_signal * (1 + 0.1 * np.random.randn(num_samples))
    
    return ecg_signal.tolist()

def create_ecg_waveform_observation(patient_id, patient_name, condition_type):
    """Create ECG observation with waveform data"""
    
    # Generate waveform (10 seconds at 500 Hz = 5000 samples)
    waveform = generate_ecg_waveform(condition_type, duration_seconds=10, sampling_rate=500)
    
    # FHIR limits data size, so we'll store every 10th sample (50 Hz effective)
    sampled_waveform = waveform[::10]  # 500 samples
    
    # Convert to space-separated string
    waveform_string = " ".join([f"{v:.3f}" for v in sampled_waveform])
    
    observation = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "procedure",
                "display": "Procedure"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "131328",
                "display": "MDC_ECG_ELEC_POTL_II"
            }],
            "text": "ECG Lead II Waveform"
        },
        "subject": {
            "reference": f"Patient/{patient_id}",
            "display": patient_name
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueSampledData": {
            "origin": {
                "value": 0,
                "unit": "mV",
                "system": "http://unitsofmeasure.org",
                "code": "mV"
            },
            "period": 20,  # milliseconds between samples (50 Hz)
            "dimensions": 1,
            "data": waveform_string
        },
        "note": [{
            "text": f"10-second ECG Lead II recording. Sampling rate: 50 Hz. Total samples: {len(sampled_waveform)}"
        }]
    }
    
    result = post_to_healthlake(observation)
    return result['id']

# Patient IDs from previous script
CARDIAC_PATIENTS = [
    {"id": "6df562fc-25a7-4e72-8753-9583e3259572", "name": "Sarah Johnson", "condition": "afib"},
    {"id": "02ddeba7-45bc-4a90-962f-6044be99005a", "name": "Robert Williams", "condition": "mi"},
    {"id": "c629b0db-4204-4cad-a9bd-7d13efdf6594", "name": "Maria Garcia", "condition": "normal"},
    {"id": "1923687c-0068-47bd-96a9-8ef34801dc9c", "name": "David Chen", "condition": "vtach"},
    {"id": "b9b10962-05fe-4912-944e-21a6ff2ae2b2", "name": "Jennifer Brown", "condition": "normal"},
]

if __name__ == "__main__":
    print("=" * 70)
    print("ADDING ECG WAVEFORM DATA FOR CARDIAC PATIENTS")
    print("=" * 70)
    
    for i, patient in enumerate(CARDIAC_PATIENTS, 1):
        print(f"\n{i}. Adding ECG waveform for {patient['name']}...")
        try:
            obs_id = create_ecg_waveform_observation(
                patient['id'], 
                patient['name'], 
                patient['condition']
            )
            print(f"   [OK] Waveform Observation ID: {obs_id}")
            print(f"   - Type: {patient['condition'].upper()}")
            print(f"   - Duration: 10 seconds")
            print(f"   - Samples: 500 data points")
        except Exception as e:
            print(f"   [ERROR] {str(e)}")
    
    print("\n" + "=" * 70)
    print("SUCCESS! ECG waveform data added")
    print("=" * 70)
    print("\nWaveform data can now be:")
    print("  - Retrieved via FHIR API")
    print("  - Visualized as time-series graphs")
    print("  - Analyzed for patterns")
    print("\nNext: Create visualization script to plot ECG waveforms")
