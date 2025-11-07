import boto3
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
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

def plot_ecg_waveforms():
    """Retrieve and plot ECG waveforms"""
    
    # Search for ECG observations with waveform data
    observations = search_healthlake('Observation', {'code': '131328', '_count': '100'})
    
    if not observations.get('entry'):
        print("No ECG waveform data found")
        return
    
    # Create subplots
    num_ecgs = min(len(observations['entry']), 5)
    fig, axes = plt.subplots(num_ecgs, 1, figsize=(12, 3*num_ecgs))
    if num_ecgs == 1:
        axes = [axes]
    
    for idx, entry in enumerate(observations['entry'][:5]):
        obs = entry['resource']
        
        # Extract waveform data
        if 'valueSampledData' in obs:
            sampled_data = obs['valueSampledData']
            data_string = sampled_data['data']
            period_ms = sampled_data['period']
            
            # Parse waveform
            waveform = [float(x) for x in data_string.split()]
            time = np.arange(len(waveform)) * period_ms / 1000  # Convert to seconds
            
            # Get patient info
            patient_ref = obs.get('subject', {}).get('display', 'Unknown Patient')
            
            # Plot
            axes[idx].plot(time, waveform, 'b-', linewidth=0.8)
            axes[idx].set_title(f'ECG Lead II - {patient_ref}', fontsize=12, fontweight='bold')
            axes[idx].set_xlabel('Time (seconds)')
            axes[idx].set_ylabel('Amplitude (mV)')
            axes[idx].grid(True, alpha=0.3)
            axes[idx].set_xlim([0, max(time)])
    
    plt.tight_layout()
    plt.savefig('ecg_waveforms.png', dpi=150, bbox_inches='tight')
    print(f"Saved ECG waveforms to: ecg_waveforms.png")
    plt.show()

if __name__ == "__main__":
    print("Retrieving and visualizing ECG waveforms...")
    plot_ecg_waveforms()
