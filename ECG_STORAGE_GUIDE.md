# Storing ECG Data in HealthLake (FHIR)

## Overview
ECG (Electrocardiogram) data can be stored in HealthLake using FHIR resources. There are multiple approaches depending on your use case.

---

## 🎯 Recommended Approaches

### **Option 1: Observation Resource (Recommended for Waveform Data)**

Store ECG as an Observation with waveform data using SampledData datatype.

**Use Case:** Store actual ECG waveform with measurements
**Pros:** Native FHIR support, queryable, structured
**Cons:** Limited to smaller datasets

```json
{
  "resourceType": "Observation",
  "id": "ecg-12-lead-001",
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
    "text": "ECG Lead II"
  },
  "subject": {
    "reference": "Patient/patient-id-here"
  },
  "effectiveDateTime": "2025-01-15T10:30:00Z",
  "valueSampledData": {
    "origin": {
      "value": 0,
      "unit": "mV",
      "system": "http://unitsofmeasure.org",
      "code": "mV"
    },
    "period": 2,
    "dimensions": 1,
    "data": "0.1 0.2 0.3 0.5 0.8 1.2 0.9 0.4 0.2 0.1"
  },
  "component": [
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8867-4",
          "display": "Heart rate"
        }]
      },
      "valueQuantity": {
        "value": 72,
        "unit": "beats/minute",
        "system": "http://unitsofmeasure.org",
        "code": "/min"
      }
    },
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8625-6",
          "display": "PR interval"
        }]
      },
      "valueQuantity": {
        "value": 160,
        "unit": "ms",
        "system": "http://unitsofmeasure.org",
        "code": "ms"
      }
    },
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8633-0",
          "display": "QRS duration"
        }]
      },
      "valueQuantity": {
        "value": 90,
        "unit": "ms",
        "system": "http://unitsofmeasure.org",
        "code": "ms"
      }
    }
  ]
}
```

---

### **Option 2: DiagnosticReport with Media (For ECG Images/PDFs)**

Store ECG report with attached image or PDF.

**Use Case:** Store ECG as image (PNG/JPG) or PDF report
**Pros:** Easy to store complete reports, supports attachments
**Cons:** Not queryable by waveform data

```json
{
  "resourceType": "DiagnosticReport",
  "id": "ecg-report-001",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
      "code": "CG",
      "display": "Cytogenetics"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "11524-6",
      "display": "EKG study"
    }],
    "text": "12-Lead ECG"
  },
  "subject": {
    "reference": "Patient/patient-id-here"
  },
  "effectiveDateTime": "2025-01-15T10:30:00Z",
  "issued": "2025-01-15T11:00:00Z",
  "conclusion": "Normal sinus rhythm. No acute ST-T wave changes.",
  "media": [{
    "comment": "12-Lead ECG Tracing",
    "link": {
      "reference": "Media/ecg-image-001"
    }
  }]
}
```

**Associated Media Resource:**
```json
{
  "resourceType": "Media",
  "id": "ecg-image-001",
  "status": "completed",
  "type": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/media-type",
      "code": "image",
      "display": "Image"
    }]
  },
  "subject": {
    "reference": "Patient/patient-id-here"
  },
  "createdDateTime": "2025-01-15T10:30:00Z",
  "content": {
    "contentType": "image/png",
    "data": "base64-encoded-image-data-here",
    "title": "12-Lead ECG"
  }
}
```

---

### **Option 3: DocumentReference (For Large ECG Files)**

Store reference to ECG file in S3 or external storage.

**Use Case:** Large ECG files, continuous monitoring data
**Pros:** Handles large files, efficient storage
**Cons:** Requires external storage (S3)

```json
{
  "resourceType": "DocumentReference",
  "id": "ecg-document-001",
  "status": "current",
  "type": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "11524-6",
      "display": "EKG study"
    }]
  },
  "subject": {
    "reference": "Patient/patient-id-here"
  },
  "date": "2025-01-15T10:30:00Z",
  "content": [{
    "attachment": {
      "contentType": "application/pdf",
      "url": "s3://my-bucket/ecg-reports/patient-001-ecg-20250115.pdf",
      "title": "12-Lead ECG Report",
      "creation": "2025-01-15T10:30:00Z"
    }
  }]
}
```

---

## 📊 Common ECG Measurements to Store

### As Observation Components:
- **Heart Rate** (LOINC: 8867-4)
- **PR Interval** (LOINC: 8625-6)
- **QRS Duration** (LOINC: 8633-0)
- **QT Interval** (LOINC: 8634-8)
- **QTc (Corrected)** (LOINC: 8636-3)
- **P Wave Duration** (LOINC: 8626-4)
- **T Wave** (LOINC: 8632-2)
- **ST Segment** (LOINC: 8631-4)

---

## 🔧 Implementation Strategy

### For Your Use Case (Cardiac Patient):

1. **Create Patient** with cardiac condition
2. **Create Condition** for cardiac problem
3. **Create Observation** for ECG with:
   - Waveform data (if available)
   - Key measurements (HR, intervals)
   - Interpretation
4. **Create DiagnosticReport** linking to Observation
5. **Optional: Media/DocumentReference** for images/PDFs

---

## 💡 Best Practices

### 1. **Use LOINC Codes**
- Standard codes for ECG measurements
- Ensures interoperability

### 2. **Link Resources**
- Link Observation to Patient
- Link DiagnosticReport to Observation
- Link to Encounter if part of visit

### 3. **Store Metadata**
- Device information
- Technician/Physician
- Location
- Timestamp

### 4. **Handle Large Data**
- Use S3 for raw waveform files
- Store summary in FHIR
- Reference external files

---

## 🚀 Quick Start: Add ECG to Existing Patient

See `add_ecg_data.py` for implementation example.

---

## 📚 Resources

- **FHIR Observation**: http://hl7.org/fhir/observation.html
- **LOINC ECG Codes**: https://loinc.org/
- **SampledData**: http://hl7.org/fhir/datatypes.html#SampledData
- **DiagnosticReport**: http://hl7.org/fhir/diagnosticreport.html
