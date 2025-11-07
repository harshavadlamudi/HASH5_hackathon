# Multi-Agentic Medical Analysis System - Design Document

## 🏥 Overview

A multi-agent system that analyzes patient data from HealthLake using three specialized medical agents (Cardiologist, Radiologist, Endocrinologist) coordinated by an orchestrator agent to generate comprehensive medical reports for doctors.

---

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Doctor/User Interface                     │
│                      (Streamlit UI)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator Agent (Supervisor)                 │
│         - Routes patient data to specialists                 │
│         - Aggregates specialist reports                      │
│         - Generates comprehensive summary                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Cardiologist │ │ Radiologist  │ │Endocrinologist│
│    Agent     │ │    Agent     │ │    Agent      │
└──────┬───────┘ └──────┬───────┘ └──────┬────────┘
       │                │                 │
       └────────────────┼─────────────────┘
                        ▼
              ┌──────────────────┐
              │  Data Retrieval  │
              │  Agent (Current) │
              │  ID: HSSKM4JAUB  │
              └─────────┬────────┘
                        ▼
              ┌──────────────────┐
              │   AWS HealthLake │
              │   (FHIR Data)    │
              └──────────────────┘
```

---

## 🤖 Agent Definitions

### 1. Orchestrator/Supervisor Agent
**Purpose**: Coordinates all specialist agents and generates final report

**Responsibilities**:
- Receives patient ID from UI
- Calls data retrieval agent to get raw FHIR data
- Routes relevant data to each specialist agent
- Aggregates all specialist reports
- Generates final comprehensive report
- Handles error cases and missing data
- Prioritizes critical findings

**Input**: Patient ID
**Output**: Comprehensive medical report with all specialist analyses

---

### 2. Cardiologist Agent
**Focus**: Cardiovascular health analysis

**Analyzes**:
- ECG waveforms (rhythm, rate, abnormalities)
- Blood pressure observations
- Cardiac conditions (AFib, MI, heart failure)
- Cardiac medications
- Cardiac MRI/imaging
- Heart rate variability
- Cardiac risk factors

**Output**: 
- Cardiac health assessment
- Risk stratification
- Treatment recommendations
- Follow-up suggestions

---

### 3. Radiologist Agent
**Focus**: Medical imaging interpretation

**Analyzes**:
- MRI images and reports
- DiagnosticReport resources
- Imaging findings and conclusions
- Anatomical abnormalities
- Image quality assessment
- Comparison with previous studies

**Output**:
- Radiology report
- Image analysis findings
- Abnormality descriptions
- Recommendations for additional imaging

---

### 4. Endocrinologist Agent
**Focus**: Hormonal and metabolic health

**Analyzes**:
- Lab results (glucose, HbA1c, thyroid)
- Diabetes-related conditions
- Metabolic observations
- Endocrine medications
- Hormone levels
- Metabolic syndrome indicators

**Output**:
- Endocrine/metabolic health report
- Lab result interpretation
- Treatment recommendations
- Lifestyle modifications

---

### 5. Data Retrieval Agent (Existing)
**Agent ID**: HSSKM4JAUB
**Alias ID**: TSTALIASID

**Purpose**: Fetch raw FHIR data from HealthLake
**Status**: Already functional - no changes needed

---

## 🔧 AWS Services Architecture

### 1. AWS Bedrock Agents
- **5 Total Agents**: Orchestrator + 3 Specialists + Data Retrieval
- **Model**: Claude 3 Sonnet
- **Region**: us-west-2

### 2. AWS Step Functions
**Purpose**: Orchestrate multi-agent workflow

**Workflow**:
```
Start
  ↓
Get Patient Data (Agent HSSKM4JAUB)
  ↓
Parallel Execution:
  ├─→ Cardiologist Agent
  ├─→ Radiologist Agent
  └─→ Endocrinologist Agent
  ↓
Wait for All (Join)
  ↓
Orchestrator Agent (Aggregate Reports)
  ↓
Generate Final Report
  ↓
Store in S3 / Return to UI
```

**Benefits**:
- Parallel specialist analysis (faster)
- Error handling and retries
- Visual workflow monitoring
- State management

---

### 3. Amazon S3
**Purpose**: Store generated reports

**Bucket Structure**:
```
s3://healthlake-reports/
  ├── patient-{id}/
  │   ├── comprehensive-report-{timestamp}.json
  │   ├── comprehensive-report-{timestamp}.pdf
  │   ├── cardiologist-report-{timestamp}.json
  │   ├── radiologist-report-{timestamp}.json
  │   └── endocrinologist-report-{timestamp}.json
```

---

### 4. Amazon DynamoDB
**Purpose**: Track report generation and status

**Table**: ReportMetadata

**Schema**:
```
{
  "patient_id": "string (PK)",
  "report_id": "string (SK)",
  "timestamp": "string",
  "status": "string (pending/completed/failed)",
  "specialist_reports": {
    "cardiology": "s3_url",
    "radiology": "s3_url",
    "endocrinology": "s3_url"
  },
  "s3_location": "string",
  "generated_by": "string"
}
```

---

### 5. Amazon EventBridge
**Purpose**: Event-driven triggers

**Events**:
- `PatientDataUpdated` → Trigger new analysis
- `ReportRequested` → Start Step Function
- `SpecialistReportCompleted` → Update status

---

### 6. AWS Lambda Functions

**Function 1: PDF Generator**
- Input: JSON report
- Output: PDF file
- Library: ReportLab or WeasyPrint

**Function 2: Data Preprocessor**
- Input: Raw FHIR data
- Output: Formatted data for specialists
- Filters relevant data per specialty

**Function 3: Report Aggregator**
- Input: All specialist reports
- Output: Combined JSON structure
- Handles missing reports

**Function 4: Notification Handler**
- Input: Report completion event
- Output: Email/SNS notification to doctor

---

### 7. Amazon Bedrock Knowledge Bases (Optional)

**Purpose**: Enhance agent intelligence with medical knowledge

**Knowledge Sources**:
- Medical guidelines (AHA, ACC, Endocrine Society)
- Drug interaction databases
- Diagnostic criteria
- Treatment protocols

---

### 8. Amazon CloudWatch
**Purpose**: Monitoring and logging

**Metrics**:
- Agent invocation times
- Report generation success rate
- Specialist agent performance
- Error rates

**Logs**:
- Agent conversations
- Step Function executions
- Lambda invocations

---

## 📊 Report Structure

```json
{
  "patient_id": "6df562fc-25a7-4e72-8753-9583e3259572",
  "patient_name": "Sarah Johnson",
  "report_date": "2025-01-31T10:30:00Z",
  "report_id": "RPT-20250131-001",
  
  "executive_summary": {
    "critical_findings": [
      "Atrial fibrillation detected on ECG",
      "Enlarged left atrium on cardiac MRI"
    ],
    "overall_assessment": "Patient presents with atrial fibrillation requiring management",
    "urgent_actions": [
      "Consider anticoagulation therapy",
      "Cardiology follow-up within 2 weeks"
    ]
  },
  
  "cardiology": {
    "agent_id": "CARDIO_AGENT_ID",
    "timestamp": "2025-01-31T10:25:00Z",
    "findings": [
      {
        "type": "ECG",
        "finding": "Irregular rhythm consistent with atrial fibrillation",
        "severity": "moderate"
      }
    ],
    "risk_assessment": "moderate",
    "recommendations": [
      "Anticoagulation therapy evaluation",
      "Rate control medication",
      "Follow-up ECG in 3 months"
    ]
  },
  
  "radiology": {
    "agent_id": "RADIO_AGENT_ID",
    "timestamp": "2025-01-31T10:26:00Z",
    "imaging_findings": [
      {
        "modality": "Cardiac MRI",
        "finding": "Enlarged left atrium",
        "measurement": "4.5 cm diameter"
      }
    ],
    "abnormalities": ["Left atrial enlargement"],
    "recommendations": [
      "Repeat MRI in 6 months",
      "Consider echocardiogram"
    ]
  },
  
  "endocrinology": {
    "agent_id": "ENDO_AGENT_ID",
    "timestamp": "2025-01-31T10:27:00Z",
    "metabolic_findings": [],
    "lab_analysis": [
      {
        "test": "Glucose",
        "value": "95 mg/dL",
        "status": "normal"
      }
    ],
    "recommendations": [
      "Continue current metabolic monitoring"
    ]
  }
}
```

---

## 🔄 Detailed Workflow

### Step-by-Step Process:

1. **Doctor selects patient** in Streamlit UI
2. **UI triggers Step Function** with patient_id
3. **Step Function starts**:
   - Invokes Data Retrieval Agent (HSSKM4JAUB)
   - Gets comprehensive FHIR data from HealthLake
4. **Parallel Specialist Analysis** (simultaneous):
   - **Cardiologist Agent**: Analyzes cardiac data
   - **Radiologist Agent**: Reviews imaging
   - **Endocrinologist Agent**: Evaluates metabolic data
5. **Each specialist** generates structured JSON report
6. **Orchestrator Agent**:
   - Receives all specialist reports
   - Identifies critical findings
   - Generates executive summary
   - Highlights urgent issues
   - Creates comprehensive report
7. **Report Storage**:
   - JSON saved to S3
   - Metadata saved to DynamoDB
   - PDF generated via Lambda
8. **UI displays**:
   - Comprehensive report
   - Individual specialist sections
   - Visualizations (ECG, MRI)
   - Recommendations
   - Download PDF option

---

## 🚀 Implementation Phases

### Phase 1: Create Specialist Agents (Week 1)
- [ ] Deploy Cardiologist Bedrock Agent
- [ ] Deploy Radiologist Bedrock Agent
- [ ] Deploy Endocrinologist Bedrock Agent
- [ ] Define specialized prompts for each
- [ ] Test with sample patient data

### Phase 2: Build Orchestrator (Week 1-2)
- [ ] Create Orchestrator Bedrock Agent
- [ ] Implement routing logic
- [ ] Test aggregation functionality
- [ ] Handle error cases

### Phase 3: Step Functions Workflow (Week 2)
- [ ] Design state machine JSON
- [ ] Implement parallel execution
- [ ] Add error handling and retries
- [ ] Test end-to-end workflow

### Phase 4: Storage & Retrieval (Week 2-3)
- [ ] Set up S3 bucket with proper structure
- [ ] Create DynamoDB table
- [ ] Implement Lambda functions (PDF, preprocessor, aggregator)
- [ ] Test storage and retrieval

### Phase 5: UI Integration (Week 3)
- [ ] Add "Generate Report" button to Streamlit
- [ ] Display specialist sections
- [ ] Show visualizations
- [ ] Add PDF download
- [ ] Implement status tracking

### Phase 6: Testing & Optimization (Week 4)
- [ ] End-to-end testing with all patients
- [ ] Performance optimization
- [ ] Cost analysis
- [ ] Documentation

---

## 🎨 UI Mockup

```
┌─────────────────────────────────────────────┐
│  Patient: Sarah Johnson                     │
│  [Generate Comprehensive Report] 🔄         │
│  Status: ⏳ Generating... (30s remaining)   │
├─────────────────────────────────────────────┤
│  📋 Executive Summary                       │
│  ⚠️  Critical: Atrial Fibrillation detected │
│  ✅ Overall: Stable condition               │
│  🚨 Urgent: Consider anticoagulation        │
├─────────────────────────────────────────────┤
│  ❤️  Cardiology Report                      │
│  └─ ECG Analysis: Irregular rhythm...       │
│  └─ Risk: Moderate                          │
│  └─ Recommendations: 3 items               │
├─────────────────────────────────────────────┤
│  🔬 Radiology Report                        │
│  └─ Cardiac MRI: Enlarged left atrium...    │
│  └─ Findings: 1 abnormality                │
├─────────────────────────────────────────────┤
│  💉 Endocrinology Report                    │
│  └─ Metabolic: Normal glucose levels...     │
│  └─ Labs: All within normal range          │
├─────────────────────────────────────────────┤
│  [Download PDF Report] 📄                   │
│  [View Previous Reports] 📚                 │
└─────────────────────────────────────────────┘
```

---

## 💡 Key Design Decisions

### Why Step Functions?
- Visual workflow representation
- Built-in error handling and retries
- Parallel execution support
- State management
- Easy monitoring

### Why Separate Specialist Agents?
- Domain-specific expertise
- Focused prompts = better accuracy
- Modular and maintainable
- Easy to add new specialists

### Why S3 + DynamoDB?
- S3: Large reports and PDFs
- DynamoDB: Fast metadata queries
- Cost-effective at scale
- Proven reliability

### Why Orchestrator Agent?
- Intelligent aggregation
- Context-aware summary
- Prioritization of findings
- Natural language synthesis
- Reduces hallucinations

---

## ⚠️ Considerations & Challenges

### 1. Cost
- Multiple agent invocations per report
- Estimate: $0.50-$2.00 per comprehensive report
- Mitigation: Cache results, batch processing

### 2. Latency
- Parallel execution: ~30-60 seconds
- Sequential would be 2-3 minutes
- Acceptable for non-urgent reports

### 3. Accuracy
- Medical domain requires high accuracy
- Mitigation: Knowledge bases, validation rules
- Human-in-the-loop for critical findings

### 4. Data Privacy
- HIPAA compliance required
- Encryption at rest and in transit
- Audit logging
- Access controls

### 5. Error Handling
- What if one specialist fails?
- Partial reports vs complete failure
- Retry logic and fallbacks

---

## 📈 Success Metrics

### Performance
- Report generation time < 60 seconds
- Success rate > 95%
- Agent accuracy > 90%

### Quality
- Doctor satisfaction score > 4/5
- Reduction in manual review time
- Actionable recommendations rate

### Cost
- Cost per report < $2.00
- ROI positive within 6 months

---

## 🔐 Security & Compliance

### HIPAA Compliance
- Encrypt all data in transit (TLS)
- Encrypt all data at rest (S3, DynamoDB)
- Audit logging (CloudTrail)
- Access controls (IAM)
- Data retention policies

### Access Control
- Role-based access (doctors only)
- Patient consent tracking
- Audit trail for all access

---

## 📚 Next Steps

1. **Review this design** with team
2. **Get approval** for AWS services
3. **Start Phase 1**: Create specialist agents
4. **Set up development environment**
5. **Begin implementation**

---

## ❓ Open Questions

1. Should reports be generated on-demand or pre-generated?
2. Do we need real-time updates or batch processing?
3. Should we add more specialists (neurologist, oncologist)?
4. Do we need human review before finalizing reports?
5. What's the expected report volume per day?

---

**Document Version**: 1.0
**Last Updated**: 2025-01-31
**Branch**: feature/multi-agentic-system
