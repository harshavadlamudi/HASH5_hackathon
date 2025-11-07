import streamlit as st
import boto3
import uuid
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from dotenv import load_dotenv
import io
import re

load_dotenv()

AGENT_ID = 'HSSKM4JAUB'
AGENT_ALIAS_ID = 'TSTALIASID'
REGION = 'us-west-2'
DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'

def invoke_agent(prompt, session_id):
    """Invoke Bedrock Agent"""
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=prompt
    )
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
    
    return completion

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

def extract_patient_id(text):
    """Extract patient ID from agent response"""
    pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    matches = re.findall(pattern, text.lower())
    return matches[0] if matches else None

def get_patient_ecg_waveform(patient_id):
    """Get ECG waveform for patient"""
    waveform_obs = search_healthlake('Observation', {'patient': patient_id, 'code': '131328', '_count': '1'})
    
    if waveform_obs.get('entry'):
        obs = waveform_obs['entry'][0]['resource']
        if 'valueSampledData' in obs:
            sampled_data = obs['valueSampledData']
            data_string = sampled_data['data']
            period_ms = sampled_data['period']
            
            waveform = [float(x) for x in data_string.split()]
            time = np.arange(len(waveform)) * period_ms / 1000
            
            patient_name = obs.get('subject', {}).get('display', 'Unknown')
            return {'time': time, 'amplitude': waveform, 'patient': patient_name}
    
    return None

def get_all_patients():
    """Fetch all patients from HealthLake"""
    result = search_healthlake('Patient', {'_count': '100'})
    patients = []
    
    if result.get('entry'):
        for entry in result['entry']:
            resource = entry['resource']
            patient_id = resource['id']
            name = 'Unknown'
            
            if 'name' in resource and resource['name']:
                name_obj = resource['name'][0]
                given = ' '.join(name_obj.get('given', []))
                family = name_obj.get('family', '')
                name = f"{given} {family}".strip()
            
            patients.append({'id': patient_id, 'name': name})
    
    return patients

def get_patient_mri_reports(patient_id):
    """Get MRI diagnostic reports for patient"""
    reports = search_healthlake('DiagnosticReport', {'patient': patient_id, '_count': '10'})
    mri_reports = []
    
    if reports.get('entry'):
        for entry in reports['entry']:
            r = entry['resource']
            report_data = {
                'type': r.get('code', {}).get('text', 'Unknown'),
                'conclusion': r.get('conclusion', 'No findings available'),
                'status': r.get('status', 'unknown'),
                'date': r.get('effectiveDateTime', 'Unknown')
            }
            mri_reports.append(report_data)
    
    return mri_reports

def get_patient_mri_images(patient_id):
    """Get MRI images for patient"""
    media = search_healthlake('Media', {'patient': patient_id, '_count': '10'})
    images = []
    
    if media.get('entry'):
        for entry in media['entry']:
            m = entry['resource']
            if 'content' in m and 'data' in m['content']:
                import base64
                image_data = base64.b64decode(m['content']['data'])
                images.append({
                    'data': image_data,
                    'title': m['content'].get('title', 'MRI Image'),
                    'type': m['content'].get('contentType', 'image/png')
                })
    
    return images

def get_patient_summary(patient_id):
    """Get comprehensive patient summary"""
    summary = {}
    
    # Get patient demographics
    patient_data = search_healthlake('Patient', {'_id': patient_id})
    if patient_data.get('entry'):
        p = patient_data['entry'][0]['resource']
        summary['name'] = 'Unknown'
        if 'name' in p and p['name']:
            name_obj = p['name'][0]
            given = ' '.join(name_obj.get('given', []))
            family = name_obj.get('family', '')
            summary['name'] = f"{given} {family}".strip()
        summary['gender'] = p.get('gender', 'Unknown')
        summary['birthDate'] = p.get('birthDate', 'Unknown')
    
    # Get conditions
    conditions = search_healthlake('Condition', {'patient': patient_id, '_count': '10'})
    summary['conditions'] = []
    if conditions.get('entry'):
        for entry in conditions['entry']:
            c = entry['resource']
            if 'code' in c and 'text' in c['code']:
                summary['conditions'].append(c['code']['text'])
    
    # Get medications
    meds = search_healthlake('MedicationRequest', {'patient': patient_id, '_count': '10'})
    summary['medications'] = []
    if meds.get('entry'):
        for entry in meds['entry']:
            m = entry['resource']
            if 'medicationCodeableConcept' in m and 'text' in m['medicationCodeableConcept']:
                summary['medications'].append(m['medicationCodeableConcept']['text'])
    
    # Get allergies
    allergies = search_healthlake('AllergyIntolerance', {'patient': patient_id, '_count': '10'})
    summary['allergies'] = []
    if allergies.get('entry'):
        for entry in allergies['entry']:
            a = entry['resource']
            if 'code' in a and 'text' in a['code']:
                summary['allergies'].append(a['code']['text'])
    
    # Get ECG data
    ecg_obs = search_healthlake('Observation', {'patient': patient_id, 'code': '131328', '_count': '1'})
    summary['has_ecg'] = bool(ecg_obs.get('entry'))
    
    # Get MRI reports
    summary['mri_reports'] = get_patient_mri_reports(patient_id)
    
    # Get MRI images
    summary['mri_images'] = get_patient_mri_images(patient_id)
    
    return summary

def plot_ecg_waveform(waveform_data):
    """Generate ECG plot"""
    fig, ax = plt.subplots(figsize=(12, 4))
    
    ax.plot(waveform_data['time'], waveform_data['amplitude'], 'b-', linewidth=1)
    ax.set_title(f"ECG Lead II - {waveform_data['patient']}", fontsize=14, fontweight='bold')
    ax.set_xlabel('Time (seconds)', fontsize=11)
    ax.set_ylabel('Amplitude (mV)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=0, color='r', linestyle='-', linewidth=0.5, alpha=0.5)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf

# Page config
st.set_page_config(
    page_title="HealthLake AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_ecg' not in st.session_state:
    st.session_state.show_ecg = False
if 'current_patient_id' not in st.session_state:
    st.session_state.current_patient_id = None
if 'patient_summary' not in st.session_state:
    st.session_state.patient_summary = None
if 'selected_view' not in st.session_state:
    st.session_state.selected_view = None

# Header
st.title("🏥 HealthLake AI Assistant with ECG Visualization")
st.markdown("Ask questions about patient health data and view ECG waveforms")

# Sidebar
with st.sidebar:
    st.header("Select Patient")
    
    # Load patients
    if 'patients' not in st.session_state:
        with st.spinner("Loading patients..."):
            st.session_state.patients = get_all_patients()
    
    if st.session_state.patients:
        patient_options = {f"{p['name']} ({p['id'][:8]}...)": p['id'] for p in st.session_state.patients}
        selected_display = st.selectbox(
            "Choose a patient:",
            options=['-- Select Patient --'] + list(patient_options.keys()),
            key='patient_selector'
        )
        
        if selected_display != '-- Select Patient --':
            selected_id = patient_options[selected_display]
            if st.session_state.current_patient_id != selected_id:
                st.session_state.current_patient_id = selected_id
                st.session_state.show_ecg = True
                st.session_state.patient_summary = None
                st.rerun()
    
    st.divider()
    
    st.header("About")
    st.info("""
    This AI assistant can:
    - Search patient records
    - View medical conditions
    - Display ECG waveforms
    - Query health data
    """)
    
    st.header("Sample Questions")
    sample_questions = [
        "Show me all patients",
        "List cardiac patients",
        "Find patients with MRI reports",
        "What are the patient's conditions?",
        "Show diagnostic reports"
    ]
    
    for q in sample_questions:
        if st.button(q, key=q):
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner("Thinking..."):
                response = invoke_agent(q, st.session_state.session_id)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                patient_id = extract_patient_id(response)
                if patient_id:
                    st.session_state.current_patient_id = patient_id
                    st.session_state.show_ecg = True
            st.rerun()
    
    st.divider()
    
    st.header("ECG Visualization")
    
    if st.session_state.current_patient_id:
        st.success(f"Patient ID: {st.session_state.current_patient_id[:8]}...")
        if st.button("Show ECG Waveform"):
            st.session_state.show_ecg = True
            st.rerun()
        if st.button("Hide ECG"):
            st.session_state.show_ecg = False
            st.rerun()
    else:
        st.info("Ask about a specific patient to view their ECG")
    
    st.divider()
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.show_ecg = False
        st.session_state.current_patient_id = None
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Show patient summary if selected
    if st.session_state.current_patient_id:
        if st.session_state.patient_summary is None:
            with st.spinner("Loading patient data..."):
                st.session_state.patient_summary = get_patient_summary(st.session_state.current_patient_id)
        
        summary = st.session_state.patient_summary
        with st.expander("📋 Patient Summary", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Name:** {summary.get('name', 'N/A')}")
                st.write(f"**Gender:** {summary.get('gender', 'N/A')}")
            with col_b:
                st.write(f"**Birth Date:** {summary.get('birthDate', 'N/A')}")
                st.write(f"**Patient ID:** {st.session_state.current_patient_id[:13]}...")
            
            if summary.get('conditions'):
                st.write(f"**Conditions:** {', '.join(summary['conditions'][:3])}")
            
            if summary.get('medications'):
                st.write(f"**Medications:** {', '.join(summary['medications'][:3])}")
            
            if summary.get('allergies'):
                st.write(f"**Allergies:** {', '.join(summary['allergies'])}")
            
            st.divider()
            
            # Show available data types
            data_types = []
            if summary.get('has_ecg'):
                data_types.append("✅ ECG Data")
            if summary.get('mri_reports'):
                data_types.append(f"✅ MRI Reports ({len(summary['mri_reports'])})")
            if summary.get('mri_images'):
                data_types.append(f"✅ MRI Images ({len(summary['mri_images'])})")
            
            if data_types:
                st.write("**Available Data:**")
                for dt in data_types:
                    st.write(dt)
            
            # Show MRI reports
            if summary.get('mri_reports'):
                st.write("**MRI Reports:**")
                for idx, report in enumerate(summary['mri_reports'], 1):
                    with st.expander(f"{report['type']} - {report['status']}"):
                        st.write(f"**Date:** {report['date'][:10] if len(report['date']) > 10 else report['date']}")
                        st.write(f"**Findings:** {report['conclusion']}")
    
    st.subheader("Chat")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about patient health data..."):
        # Add patient context if a patient is selected
        if st.session_state.current_patient_id:
            contextualized_prompt = f"For patient ID {st.session_state.current_patient_id}: {prompt}"
        else:
            contextualized_prompt = prompt
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing health data..."):
                response = invoke_agent(contextualized_prompt, st.session_state.session_id)
                st.markdown(response)
                
                patient_id = extract_patient_id(response)
                if patient_id and not st.session_state.current_patient_id:
                    st.session_state.current_patient_id = patient_id
                    st.session_state.show_ecg = True
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    st.subheader("Medical Data Visualization")
    
    if st.session_state.current_patient_id:
        if st.session_state.patient_summary:
            has_ecg = st.session_state.patient_summary.get('has_ecg', False)
            has_mri_images = bool(st.session_state.patient_summary.get('mri_images'))
            
            # Data type selector
            view_options = []
            if has_ecg:
                view_options.append("ECG Waveform")
            if has_mri_images:
                view_options.append("MRI Images")
            
            if view_options:
                selected_view = st.radio("Select View:", view_options, horizontal=True)
                
                st.divider()
                
                if selected_view == "ECG Waveform" and has_ecg:
                    with st.spinner("Loading ECG data..."):
                        waveform = get_patient_ecg_waveform(st.session_state.current_patient_id)
                        
                        if waveform:
                            st.success(f"ECG - {waveform['patient']}")
                            
                            ecg_plot = plot_ecg_waveform(waveform)
                            st.image(ecg_plot, use_container_width=True)
                            
                            col_m1, col_m2 = st.columns(2)
                            with col_m1:
                                st.metric("Duration", f"{max(waveform['time']):.1f}s")
                            with col_m2:
                                st.metric("Samples", len(waveform['amplitude']))
                
                elif selected_view == "MRI Images" and has_mri_images:
                    mri_images = st.session_state.patient_summary.get('mri_images', [])
                    
                    for idx, img in enumerate(mri_images):
                        st.success(f"{img['title']}")
                        st.image(img['data'], use_container_width=True)
                        if idx < len(mri_images) - 1:
                            st.divider()
            else:
                st.info("💡 No ECG or MRI imaging data available")
        else:
            st.info("💡 Select a patient to view their medical data")
    else:
        st.info("💡 Select a patient from the dropdown")
        st.markdown("""
        **Available data types:**
        - ECG waveforms
        - MRI images
        - Diagnostic reports
        - Medical conditions
        """)
