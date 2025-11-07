import streamlit as st
import boto3
import uuid
from dotenv import load_dotenv
from get_patient_names import get_all_patients

load_dotenv()

DOCTOR_AGENT_ID = 'HSSKM4JAUB'
DOCTOR_AGENT_ALIAS_ID = 'TSTALIASID'
PATIENT_AGENT_ID = '67SSNLYIOJ'
PATIENT_AGENT_ALIAS_ID = '7XNB3AYIYK'
REGION = 'us-west-2'

def invoke_doctor_agent(prompt, session_id):
    """Invoke doctor agent for data retrieval"""
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    response = runtime.invoke_agent(
        agentId=DOCTOR_AGENT_ID,
        agentAliasId=DOCTOR_AGENT_ALIAS_ID,
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

def invoke_patient_agent_with_data(prompt, patient_name, patient_id, session_id):
    """Get data from doctor agent, then explain via patient agent"""
    runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
    
    # Step 1: Get raw data from doctor agent using patient ID
    data_query = f"Get detailed information for patient ID {patient_id} including conditions, medications, and vital signs"
    raw_data = invoke_doctor_agent(data_query, session_id + "_doctor")
    
    # Step 2: Send to patient agent for simple explanation
    patient_prompt = f"""Patient {patient_name} asked: {prompt}

Here is their medical data:
{raw_data}

Please explain this information in simple, friendly terms that the patient can easily understand. Avoid medical jargon."""
    
    response = runtime.invoke_agent(
        agentId=PATIENT_AGENT_ID,
        agentAliasId=PATIENT_AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=patient_prompt
    )
    
    completion = ""
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
    
    return completion

st.set_page_config(page_title="HealthLake AI Assistant", page_icon="🏥", layout="wide")

if 'mode' not in st.session_state:
    st.session_state.mode = 'doctor'
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏥 HealthLake AI Assistant")
with col2:
    mode = st.radio("Mode:", ["👨⚕️ Doctor", "🩺 Patient"], horizontal=True, label_visibility="collapsed")
    new_mode = 'doctor' if mode == "👨⚕️ Doctor" else 'patient'
    
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

if st.session_state.mode == 'doctor':
    st.markdown("**Doctor Mode** - Query patient health data from HealthLake")
    
    with st.sidebar:
        st.header("📊 Doctor Mode")
        st.info("""
        Access comprehensive patient data:
        - Search patients
        - View medical conditions
        - Check vital signs & lab results
        - Query medications & procedures
        - Review care plans
        """)
        
        st.header("Sample Queries")
        samples = [
            "Show me a list of patients",
            "What medical conditions are in the system?",
            "Show me medication prescriptions",
            "List healthcare visits",
            "What allergies do patients have?",
            "Display lab reports"
        ]
        
        for q in samples:
            if st.button(q, key=q):
                st.session_state.messages.append({"role": "user", "content": q})
                with st.spinner("Querying HealthLake..."):
                    response = invoke_doctor_agent(q, st.session_state.session_id)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about patient health data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing health data..."):
                response = invoke_doctor_agent(prompt, st.session_state.session_id)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

else:  # patient mode
    st.markdown("**Patient Mode** - Understand your health information in simple terms")
    
    @st.cache_data(ttl=300)
    def load_patients():
        return get_all_patients()
    
    patient_map = load_patients()
    patient_list = sorted(patient_map.keys())
    
    if 'patient_name' not in st.session_state:
        st.session_state.patient_name = ''
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if patient_list:
            patient_name = st.selectbox(
                "👤 Select your name:",
                options=[''] + patient_list,
                index=0 if not st.session_state.patient_name else (patient_list.index(st.session_state.patient_name) + 1 if st.session_state.patient_name in patient_list else 0),
                placeholder="Choose your name from the list"
            )
        else:
            patient_name = st.text_input("👤 Enter your name:", value=st.session_state.patient_name, placeholder="e.g., John Smith")
    
    with col2:
        if st.button("🔄 Refresh List"):
            st.cache_data.clear()
            st.rerun()
    
    if patient_name != st.session_state.patient_name:
        st.session_state.patient_name = patient_name
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
    
    if not patient_name:
        st.info("👆 Please select your name from the dropdown to access your health information.")
        if patient_list:
            st.caption(f"📋 {len(patient_list)} patients available in the system")
        st.stop()
    
    patient_id = patient_map.get(patient_name)
    st.success(f"✓ Viewing health information for: **{patient_name}** (ID: {patient_id})")
    
    with st.sidebar:
        st.header("🩺 Patient Mode")
        st.info(f"""
        Viewing data for: **{patient_name}**
        
        I retrieve your data from the medical system and explain it in simple terms!
        
        I can help you understand:
        - Your care plan
        - Your medical conditions
        - Your medications
        - Your vital signs
        """)
        
        st.header("Sample Questions")
        samples = [
            "What's my health status?",
            "Explain my medical conditions",
            "What medications am I taking?",
            "Tell me about my care plan",
            "What are my vital signs?"
        ]
        
        for q in samples:
            if st.button(q, key=q):
                st.session_state.messages.append({"role": "user", "content": q})
                with st.spinner("Getting your data and explaining it..."):
                    response = invoke_patient_agent_with_data(q, patient_name, patient_id, st.session_state.session_id)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask me about your health information..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Getting your data and explaining it..."):
                response = invoke_patient_agent_with_data(prompt, patient_name, patient_id, st.session_state.session_id)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
