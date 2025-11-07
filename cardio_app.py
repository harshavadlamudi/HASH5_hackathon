import streamlit as st
import boto3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# HealthLake configuration
DATASTORE_ID = 'b4e3d8f5c2a1b9e7d6f8a2c4e1b3d5f7'

class CardioDataFetcher:
    def __init__(self):
        self.healthlake = boto3.client('healthlake', region_name='us-west-2')
    
    def get_cardio_observations(self):
        """Fetch cardiovascular observations from HealthLake"""
        try:
            response = self.healthlake.search_with_get(
                DatastoreId=DATASTORE_ID,
                ResourceType='Observation',
                SearchParameters={
                    'code': 'http://loinc.org|8480-6,http://loinc.org|8462-4,http://loinc.org|8867-4'  # BP systolic, diastolic, heart rate
                }
            )
            return response.get('ResourceList', [])
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return []
    
    def get_patients_with_cardio_conditions(self):
        """Fetch patients with cardiovascular conditions"""
        try:
            response = self.healthlake.search_with_get(
                DatastoreId=DATASTORE_ID,
                ResourceType='Condition',
                SearchParameters={
                    'code': 'hypertension,heart,cardiac,cardiovascular'
                }
            )
            return response.get('ResourceList', [])
        except Exception as e:
            st.error(f"Error fetching conditions: {e}")
            return []

def parse_observation_data(observations):
    """Parse FHIR observations into DataFrame"""
    data = []
    for obs in observations:
        try:
            patient_id = obs.get('subject', {}).get('reference', '').split('/')[-1]
            code = obs.get('code', {}).get('coding', [{}])[0].get('display', 'Unknown')
            value = obs.get('valueQuantity', {}).get('value')
            unit = obs.get('valueQuantity', {}).get('unit', '')
            date = obs.get('effectiveDateTime', obs.get('issued', ''))
            
            if value and date:
                data.append({
                    'patient_id': patient_id,
                    'measurement': code,
                    'value': float(value),
                    'unit': unit,
                    'date': pd.to_datetime(date)
                })
        except Exception:
            continue
    return pd.DataFrame(data)

def create_bp_trend_chart(df):
    """Create blood pressure trend chart"""
    bp_data = df[df['measurement'].str.contains('Blood pressure|systolic|diastolic', case=False, na=False)]
    if bp_data.empty:
        return None
    
    fig = px.line(bp_data, x='date', y='value', color='measurement', 
                  title='Blood Pressure Trends Over Time',
                  labels={'value': 'mmHg', 'date': 'Date'})
    return fig

def create_heart_rate_chart(df):
    """Create heart rate chart"""
    hr_data = df[df['measurement'].str.contains('Heart rate', case=False, na=False)]
    if hr_data.empty:
        return None
    
    fig = px.scatter(hr_data, x='date', y='value', color='patient_id',
                     title='Heart Rate by Patient',
                     labels={'value': 'BPM', 'date': 'Date'})
    return fig

def create_patient_summary_chart(df):
    """Create patient summary statistics"""
    if df.empty:
        return None
    
    summary = df.groupby(['patient_id', 'measurement'])['value'].agg(['mean', 'min', 'max']).reset_index()
    
    fig = px.bar(summary, x='patient_id', y='mean', color='measurement',
                 title='Average Cardiovascular Measurements by Patient',
                 labels={'mean': 'Average Value', 'patient_id': 'Patient ID'})
    return fig

def main():
    st.set_page_config(page_title="Cardio Data Visualizer", layout="wide")
    
    st.title("🫀 Cardiovascular Data Visualizer")
    st.markdown("Generate graphs and insights from patient cardiovascular data")
    
    # Initialize data fetcher
    fetcher = CardioDataFetcher()
    
    # Sidebar controls
    st.sidebar.header("Controls")
    refresh_data = st.sidebar.button("Refresh Data")
    
    # Chart selection
    chart_types = st.sidebar.multiselect(
        "Select Charts to Display",
        ["Blood Pressure Trends", "Heart Rate Analysis", "Patient Summary"],
        default=["Blood Pressure Trends", "Heart Rate Analysis"]
    )
    
    # Main content
    if refresh_data or 'cardio_data' not in st.session_state:
        with st.spinner("Fetching cardiovascular data..."):
            observations = fetcher.get_cardio_observations()
            conditions = fetcher.get_patients_with_cardio_conditions()
            
            if observations:
                df = parse_observation_data(observations)
                st.session_state.cardio_data = df
                st.success(f"Loaded {len(df)} cardiovascular measurements")
            else:
                st.warning("No cardiovascular data found")
                st.session_state.cardio_data = pd.DataFrame()
    
    df = st.session_state.get('cardio_data', pd.DataFrame())
    
    if not df.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Measurements", len(df))
        with col2:
            st.metric("Unique Patients", df['patient_id'].nunique())
        with col3:
            st.metric("Measurement Types", df['measurement'].nunique())
        with col4:
            st.metric("Date Range", f"{(df['date'].max() - df['date'].min()).days} days")
        
        # Display selected charts
        if "Blood Pressure Trends" in chart_types:
            bp_chart = create_bp_trend_chart(df)
            if bp_chart:
                st.plotly_chart(bp_chart, use_container_width=True)
        
        if "Heart Rate Analysis" in chart_types:
            hr_chart = create_heart_rate_chart(df)
            if hr_chart:
                st.plotly_chart(hr_chart, use_container_width=True)
        
        if "Patient Summary" in chart_types:
            summary_chart = create_patient_summary_chart(df)
            if summary_chart:
                st.plotly_chart(summary_chart, use_container_width=True)
        
        # Data table
        with st.expander("View Raw Data"):
            st.dataframe(df)
    
    else:
        st.info("No data available. Click 'Refresh Data' to load cardiovascular measurements.")

if __name__ == "__main__":
    main()