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
            st.rerun()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.show_ecg = False
        st.session_state.current_patient_id = None
        st.rerun()

# Chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about patient health data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing health data..."):
            response = invoke_agent(prompt, st.session_state.session_id)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
