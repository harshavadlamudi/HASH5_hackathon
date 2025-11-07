# Sarah Johnson - Complete Patient Data

## Patient Information
- **Patient ID**: `6df562fc-25a7-4e72-8753-9583e3259572`
- **Name**: Sarah Ann Johnson
- **Condition**: Atrial fibrillation

## Available Data

### 1. ECG Waveform Data ✅
- **Type**: 12-Lead Electrocardiogram
- **Observations**: 2 ECG observations including waveform data
- **Format**: SampledData (500 samples, 10 seconds, 50Hz)
- **View**: Select "ECG Waveform" in the UI

### 2. Cardiac MRI ✅
- **Type**: Cardiac MRI
- **DiagnosticReport**: "Enlarged left atrium consistent with atrial fibrillation. Normal ventricular function."
- **Media**: Cardiac MRI image (PNG format, base64 encoded)
- **View**: Select "MRI Images" in the UI

## How to Visualize in UI

1. **Open Streamlit App**:
   ```bash
   streamlit run app.py
   ```

2. **Select Patient**:
   - In the sidebar dropdown, select "Sarah Ann Johnson"
   - Patient summary will load automatically

3. **View ECG**:
   - In the right panel, select radio button "ECG Waveform"
   - ECG waveform will display with metrics

4. **View MRI**:
   - In the right panel, select radio button "MRI Images"
   - Cardiac MRI image will display

5. **Ask Questions**:
   - "What are the ECG findings?"
   - "Show me the MRI report"
   - "What does the cardiac MRI show?"
   - "What is the patient's condition?"

## Patient Summary Display

When Sarah Johnson is selected, you'll see:
- ✅ ECG Data
- ✅ MRI Reports (2)
- ✅ MRI Images (1)

## Complete Resource List

- **Patient**: Demographics
- **Condition**: Atrial fibrillation
- **Observation**: ECG waveform (2)
- **DiagnosticReport**: 12-Lead ECG + Cardiac MRI (2)
- **Media**: Cardiac MRI image (1)

## Use Case

Sarah Johnson is the perfect example patient to demonstrate:
- Multi-modal medical imaging (ECG + MRI)
- Cardiac patient with comprehensive data
- Both waveform data and static images
- Complete diagnostic reports

This patient showcases the full capabilities of the HealthLake AI Assistant!
