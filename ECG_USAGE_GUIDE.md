# ECG Data - Usage Guide

## 🎯 What Was Built

### 1. ECG Data Storage
- **5 cardiac patients** with complete medical history
- **ECG waveform data** (10 seconds, 500 samples per patient)
- **ECG measurements** (Heart Rate, PR, QRS, QT intervals)
- **Diagnostic reports** with clinical interpretations

### 2. Visualization Tools
- **Standalone script**: `patient_cardiac_history.py`
- **Enhanced Streamlit app**: `enhanced_app.py`
- **Batch visualization**: `visualize_ecg_waveforms.py`

### 3. Agent Capabilities
- Search patients by name
- Retrieve cardiac history
- Access ECG measurements
- Query diagnostic reports

---

## 📊 Available Cardiac Patients

| Patient | Condition | Patient ID |
|---------|-----------|------------|
| Robert Williams | Myocardial Infarction | 02ddeba7-45bc-4a90-962f-6044be99005a |
| Maria Garcia | Heart Failure | c629b0db-4204-4cad-a9bd-7d13efdf6594 |
| David Chen | Ventricular Tachycardia | 1923687c-0068-47bd-96a9-8ef34801dc9c |
| Jennifer Brown | Coronary Artery Disease | b9b10962-05fe-4912-944e-21a6ff2ae2b2 |
| Sarah Johnson | Atrial Fibrillation | 6df562fc-25a7-4e72-8753-9583e3259572 |

---

## 🚀 How to Use

### Option 1: Enhanced Streamlit App (Recommended)

```bash
streamlit run enhanced_app.py
```

**Features:**
- Chat with AI agent
- Automatic ECG visualization when querying patients
- Side-by-side chat and ECG display
- Real-time waveform rendering

**Example Queries:**
```
- "Find patient Robert Williams"
- "Show me cardiac patients"
- "Display ECG for patient 02ddeba7"
- "What is Robert Williams' cardiac history?"
```

---

### Option 2: Standalone History Report

```bash
python patient_cardiac_history.py
```

**Generates:**
- Complete patient demographics
- All cardiac conditions
- ECG measurements
- Diagnostic reports
- ECG waveform visualization (saved as PNG)

**To query different patients:**
Edit line 183 in `patient_cardiac_history.py`:
```python
selected_patient = "02ddeba7-45bc-4a90-962f-6044be99005a"  # Change this ID
```

---

### Option 3: Agent Queries (Command Line)

```bash
python -c "from test_all_resources import invoke_agent; print(invoke_agent('Find patient Robert Williams and show his cardiac history'))"
```

**Example Queries:**
```bash
# Search by name
python -c "from test_all_resources import invoke_agent; print(invoke_agent('Find patient David Chen'))"

# Get cardiac conditions
python -c "from test_all_resources import invoke_agent; print(invoke_agent('Show me patients with heart failure'))"

# Get ECG data
python -c "from test_all_resources import invoke_agent; print(invoke_agent('What ECG data is available?'))"
```

---

## 📈 ECG Waveform Details

### Data Format
- **Duration**: 10 seconds
- **Sampling Rate**: 50 Hz (effective)
- **Total Samples**: 500 data points
- **Storage**: FHIR `SampledData` datatype
- **LOINC Code**: 131328 (MDC_ECG_ELEC_POTL_II)

### Waveform Characteristics

**Normal Sinus Rhythm:**
- Regular P-QRS-T pattern
- Heart rate: 72-88 bpm
- Normal intervals

**Atrial Fibrillation:**
- Irregular rhythm
- No distinct P waves
- Heart rate: 110 bpm

**Myocardial Infarction:**
- ST segment elevation
- Heart rate: 95 bpm
- Widened QRS

**Ventricular Tachycardia:**
- Wide QRS complexes
- Rapid rate: 145 bpm
- Regular rhythm

---

## 🔧 Technical Implementation

### How ECG is Stored in HealthLake

```json
{
  "resourceType": "Observation",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "131328",
      "display": "MDC_ECG_ELEC_POTL_II"
    }]
  },
  "valueSampledData": {
    "origin": {"value": 0, "unit": "mV"},
    "period": 20,
    "dimensions": 1,
    "data": "0.1 0.2 0.3 ... (500 values)"
  }
}
```

### How to Query ECG Data

**Via FHIR API:**
```python
from explore_healthlake import HealthLakeExplorer
explorer = HealthLakeExplorer('datastore-id')
waveforms = explorer.search_resources('Observation', {'code': '131328'})
```

**Via Agent:**
```python
from test_all_resources import invoke_agent
response = invoke_agent('Show me ECG waveforms')
```

---

## 📝 Adding More Patients

### Add Single Patient with ECG:
```bash
python add_ecg_data.py
```

### Add Multiple Cardiac Patients:
```bash
python add_multiple_cardiac_patients.py
```

### Add Waveform Data:
```bash
python add_ecg_waveform_data.py
```

---

## 🎨 Visualization Examples

### Generate All ECG Waveforms:
```bash
python visualize_ecg_waveforms.py
```
Output: `ecg_waveforms.png`

### Generate Patient-Specific ECG:
```bash
python patient_cardiac_history.py
```
Output: `patient_{id}_ecg.png`

---

## 💡 Tips

1. **Patient IDs**: Use first 8 characters for queries (e.g., "02ddeba7")
2. **Name Search**: Agent can now search by first name, last name, or full name
3. **ECG Auto-Display**: Enhanced app automatically shows ECG when patient ID is detected
4. **Multiple Views**: Can view ECG measurements AND waveforms together

---

## 🔍 Troubleshooting

**Issue: "Patient not found"**
- Use exact name: "Robert Williams" not "robert williams"
- Or use patient ID directly

**Issue: "No ECG waveform data"**
- Only 5 cardiac patients have waveform data
- Run `add_ecg_waveform_data.py` to add more

**Issue: "ECG not showing in app"**
- Make sure patient ID is in the response
- Check sidebar for "Show ECG Waveform" button

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `enhanced_app.py` | Streamlit app with ECG visualization |
| `patient_cardiac_history.py` | Complete patient history report |
| `add_ecg_data.py` | Add single patient with ECG |
| `add_multiple_cardiac_patients.py` | Add 5 cardiac patients |
| `add_ecg_waveform_data.py` | Add waveform time-series data |
| `visualize_ecg_waveforms.py` | Batch ECG visualization |
| `ECG_STORAGE_GUIDE.md` | Technical storage documentation |

---

## 🎯 Next Steps

1. ✅ ECG data stored in HealthLake
2. ✅ Visualization working
3. ✅ Agent can query by name
4. 🔄 Add more patients
5. 🔄 Real-time ECG streaming
6. 🔄 ECG analysis algorithms
7. 🔄 Comparison views

---

**Built with AWS HealthLake, Bedrock Agent, and Streamlit**
