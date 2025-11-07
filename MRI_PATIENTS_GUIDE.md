# MRI Patients Guide

## Overview
This guide provides information about the 5 MRI patients added to the HealthLake datastore with diagnostic reports and MRI images.

## Available MRI Patients

### 1. Michael Anderson
- **Patient ID**: `6f0bc274-9b4e-4cc0-80eb-d49aa2f6da9a`
- **Gender**: Male
- **Birth Date**: 1965-03-15
- **Condition**: Brain tumor (glioblastoma)
- **MRI Type**: Brain MRI
- **Findings**: 4.2 cm mass in right frontal lobe with surrounding edema and mass effect
- **Media ID**: `9b254d86-4619-42a8-888f-e3ddc9a9387a`

### 2. Patricia Martinez
- **Patient ID**: `89698d95-8e01-4d88-8f00-945372d5aac9`
- **Gender**: Female
- **Birth Date**: 1972-08-22
- **Condition**: Multiple sclerosis
- **MRI Type**: Brain and Spine MRI
- **Findings**: Multiple periventricular white matter lesions consistent with demyelinating disease
- **Media ID**: `64e84732-364f-4636-9737-e5d667aaee89`

### 3. James Thompson
- **Patient ID**: `3ac6d9cb-e28f-4322-af37-86704edc03c3`
- **Gender**: Male
- **Birth Date**: 1958-11-30
- **Condition**: Lumbar disc herniation
- **MRI Type**: Lumbar Spine MRI
- **Findings**: L4-L5 disc herniation with nerve root compression
- **Media ID**: `2ac322ee-eb34-4e9b-b11f-c8b472e9a49d`

### 4. Linda Davis
- **Patient ID**: `db2dca16-3c5f-47e4-98dd-63bcc491e6ac`
- **Gender**: Female
- **Birth Date**: 1980-05-18
- **Condition**: Meniscal tear
- **MRI Type**: Knee MRI
- **Findings**: Medial meniscus tear with joint effusion
- **Media ID**: `527eba7e-a19b-4f66-9010-9f284a34d5f1`

### 5. Robert Wilson
- **Patient ID**: `a1532ebb-26bf-42c4-a523-ab56d9d76369`
- **Gender**: Male
- **Birth Date**: 1955-09-07
- **Condition**: Stroke (ischemic)
- **MRI Type**: Brain MRI with DWI
- **Findings**: Acute infarct in left middle cerebral artery territory
- **Media ID**: `fb7c8f66-1bb9-40b3-b25b-87b4d04914ca`

## Usage Examples

### Query MRI Patients via Agent

```
"Show me patients with MRI reports"
"Find patient Michael Anderson"
"What are the MRI findings for patient 6f0bc274?"
"Show diagnostic reports for Patricia Martinez"
"List patients with brain conditions"
```

### Query via Streamlit App

1. Select patient from dropdown menu
2. Patient summary will display automatically
3. Ask questions like:
   - "What are the MRI findings?"
   - "Show me the diagnostic report"
   - "What condition does this patient have?"

## FHIR Resources Created

For each MRI patient, the following resources were created:

1. **Patient** - Demographics and basic information
2. **Condition** - Medical diagnosis
3. **DiagnosticReport** - MRI study with findings
4. **Media** - MRI image (base64 encoded PNG)

## Technical Details

### DiagnosticReport Structure
```json
{
  "resourceType": "DiagnosticReport",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "24627-2",
      "display": "MRI Study"
    }],
    "text": "Brain MRI"
  },
  "subject": {"reference": "Patient/{patient_id}"},
  "conclusion": "MRI findings text",
  "presentedForm": [{
    "contentType": "text/plain",
    "data": "Report data",
    "title": "MRI Report"
  }]
}
```

## Querying MRI Data

### Search Diagnostic Reports
```python
search_healthlake('DiagnosticReport', {'patient': patient_id})
```

### Search MRI Images
```python
search_healthlake('Media', {'patient': patient_id})
```

### Decode MRI Image
```python
import base64
image_data = base64.b64decode(media_resource['content']['data'])
```

## Integration with Streamlit App

The MRI patients are now available in the patient dropdown selector. When selected:
- Patient summary displays demographics, conditions, and available data
- MRI images are displayed in the visualization panel
- Radio button to switch between ECG and MRI views
- Agent queries are automatically contextualized to the selected patient
- Diagnostic reports can be queried through natural language

## Next Steps

Future enhancements could include:
- Add real DICOM MRI images
- 3D MRI visualization
- Compare MRI scans over time
- AI-powered radiology report generation
- Image annotation and measurement tools
