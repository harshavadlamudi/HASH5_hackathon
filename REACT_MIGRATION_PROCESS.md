# React Migration Process Document

## Overview
Migrate HealthLake AI Assistant from Streamlit to React + FastAPI, deployed entirely on AWS.

---

## Current State

### What We Have (Streamlit)
- ✅ Multi-agent system (5 Bedrock agents)
- ✅ Patient selection and data display
- ✅ Comprehensive report generation (4 specialists)
- ✅ Interactive Q&A system with dynamic UI
- ✅ ECG/MRI visualization
- ✅ Progress indicators
- ✅ Conversation history

### Tech Stack (Current)
- Frontend: Streamlit (Python)
- Backend: Integrated (boto3, direct AWS calls)
- Deployment: Local/Streamlit Cloud
- State: Session state (in-memory)

---

## Target State

### What We'll Build (React)
- ✅ Modern React UI with TypeScript
- ✅ RESTful API backend (FastAPI)
- ✅ AWS deployment (S3 + CloudFront + Lambda)
- ✅ Persistent storage (DynamoDB + S3)
- ✅ Better UX (no page reloads, animations)
- ✅ Production-ready architecture

### Tech Stack (Target)
```
Frontend:
├── React 18 + TypeScript
├── Material-UI (MUI)
├── Zustand (state management)
├── Axios (HTTP client)
├── Recharts (visualizations)
└── React Router (navigation)

Backend:
├── FastAPI (Python)
├── Pydantic (validation)
├── boto3 (AWS SDK)
├── python-dotenv (config)
└── uvicorn (ASGI server)

Infrastructure:
├── AWS S3 + CloudFront (frontend)
├── AWS Lambda + API Gateway (backend)
├── AWS DynamoDB (cache)
├── AWS S3 (reports storage)
└── AWS CDK (infrastructure as code)
```

---

## Migration Strategy

### Approach: Parallel Development
- Keep Streamlit app running (don't break existing)
- Build React + FastAPI alongside
- Test thoroughly before switching
- Gradual cutover

### NOT: Big Bang Rewrite
- ❌ Don't delete Streamlit immediately
- ❌ Don't stop feature development
- ❌ Don't deploy untested code

---

## Implementation Phases

### Phase 1: Backend API Foundation (Week 1)
**Goal:** Create FastAPI backend that replicates Streamlit functionality

**Deliverables:**
1. FastAPI project structure
2. Patient management endpoints
3. HealthLake integration service
4. Basic error handling
5. API documentation (auto-generated)

**Files to Create:**
```
backend/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuration
│   ├── api/
│   │   └── routes/
│   │       ├── patients.py        # Patient endpoints
│   │       └── health.py          # Health check
│   ├── services/
│   │   └── healthlake_service.py  # HealthLake queries
│   └── models/
│       └── patient.py             # Pydantic models
├── requirements.txt
└── README.md
```

**Endpoints:**
- `GET /api/health` - Health check
- `GET /api/patients` - List all patients
- `GET /api/patients/{id}` - Get patient details
- `GET /api/patients/{id}/summary` - Get patient summary

**Success Criteria:**
- ✅ API runs locally
- ✅ Can fetch patients from HealthLake
- ✅ Swagger docs accessible at `/docs`
- ✅ All endpoints return valid JSON

---

### Phase 2: Report Generation API (Week 1-2)
**Goal:** Implement multi-agent report generation via API

**Deliverables:**
1. Bedrock agent integration service
2. Report generation endpoints
3. S3 storage for reports
4. Async job processing

**Files to Create:**
```
backend/app/
├── api/routes/
│   └── reports.py                 # Report endpoints
├── services/
│   ├── bedrock_service.py         # Bedrock agent calls
│   ├── s3_service.py              # S3 storage
│   └── report_generator.py        # Report orchestration
└── models/
    └── report.py                  # Report models
```

**Endpoints:**
- `POST /api/reports/generate` - Start report generation (returns jobId)
- `GET /api/reports/status/{jobId}` - Check generation status
- `GET /api/reports/{jobId}` - Get completed report
- `GET /api/reports/patient/{patientId}` - Get all patient reports

**Success Criteria:**
- ✅ Can invoke all 4 specialist agents
- ✅ Reports saved to S3
- ✅ Async processing works
- ✅ Progress updates available

---

### Phase 3: Q&A System API (Week 2)
**Goal:** Implement interactive Q&A via API

**Deliverables:**
1. Q&A agent integration
2. DynamoDB for conversation history
3. Dynamic UI response formatting

**Files to Create:**
```
backend/app/
├── api/routes/
│   └── qa.py                      # Q&A endpoints
├── services/
│   ├── qa_service.py              # Q&A agent calls
│   └── dynamodb_service.py        # DynamoDB operations
└── models/
    └── qa.py                      # Q&A models
```

**Endpoints:**
- `POST /api/qa/ask` - Ask question about cached report
- `GET /api/qa/history/{patientId}` - Get conversation history
- `DELETE /api/qa/history/{patientId}` - Clear history

**Success Criteria:**
- ✅ Q&A agent responds correctly
- ✅ History persisted in DynamoDB
- ✅ Returns structured UI data

---

### Phase 4: React Frontend Setup (Week 2)
**Goal:** Create React app structure and basic layout

**Deliverables:**
1. React project with TypeScript
2. Routing setup
3. Layout components (Header, Sidebar, Footer)
4. API service layer
5. State management setup

**Files to Create:**
```
frontend/
├── public/
├── src/
│   ├── components/
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── services/
│   │   └── api.ts                 # Axios instance
│   ├── store/
│   │   └── index.ts               # Zustand store
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

**Success Criteria:**
- ✅ React app runs locally
- ✅ Can call backend API
- ✅ Basic layout renders
- ✅ Routing works

---

### Phase 5: Patient Management UI (Week 2-3)
**Goal:** Build patient selection and display

**Deliverables:**
1. Patient list component
2. Patient card component
3. Patient detail view
4. Search and filter

**Files to Create:**
```
frontend/src/
├── components/
│   └── PatientSelector/
│       ├── PatientSelector.tsx
│       ├── PatientCard.tsx
│       ├── PatientList.tsx
│       └── PatientDetail.tsx
├── services/
│   └── patientService.ts
├── store/
│   └── usePatientStore.ts
└── pages/
    └── Dashboard.tsx
```

**Success Criteria:**
- ✅ Can view all patients
- ✅ Can select a patient
- ✅ Patient details display
- ✅ Search works

---

### Phase 6: Report Generation UI (Week 3)
**Goal:** Build report generation interface

**Deliverables:**
1. Report generator component
2. Progress indicator
3. Report tabs (4 specialists)
4. Report viewer

**Files to Create:**
```
frontend/src/
├── components/
│   └── ReportGenerator/
│       ├── ReportGenerator.tsx
│       ├── ProgressIndicator.tsx
│       ├── ReportTabs.tsx
│       └── ReportViewer.tsx
├── services/
│   └── reportService.ts
└── store/
    └── useReportStore.ts
```

**Success Criteria:**
- ✅ Can generate reports
- ✅ Progress updates display
- ✅ Reports display in tabs
- ✅ Can view past reports

---

### Phase 7: Q&A Interface UI (Week 3)
**Goal:** Build interactive Q&A interface

**Deliverables:**
1. Q&A interface component
2. Quick question buttons
3. Dynamic UI renderer (7 component types)
4. Conversation history

**Files to Create:**
```
frontend/src/
├── components/
│   ├── QAInterface/
│   │   ├── QAInterface.tsx
│   │   ├── QuickQuestions.tsx
│   │   ├── QuestionInput.tsx
│   │   └── ConversationHistory.tsx
│   └── DynamicUI/
│       ├── RiskAssessment.tsx
│       ├── ComparisonTable.tsx
│       ├── Timeline.tsx
│       ├── ActionItems.tsx
│       ├── DetailedCard.tsx
│       ├── KeyFindings.tsx
│       └── MedicationMap.tsx
├── services/
│   └── qaService.ts
└── store/
    └── useQAStore.ts
```

**Success Criteria:**
- ✅ Can ask questions
- ✅ Quick questions work
- ✅ Dynamic UI renders correctly
- ✅ History persists

---

### Phase 8: Visualizations (Week 3-4)
**Goal:** Build ECG and MRI visualizations

**Deliverables:**
1. ECG chart component
2. MRI image viewer
3. Vital signs charts

**Files to Create:**
```
frontend/src/
└── components/
    └── Visualizations/
        ├── ECGChart.tsx
        ├── MRIViewer.tsx
        └── VitalSignsChart.tsx
```

**Success Criteria:**
- ✅ ECG waveform displays
- ✅ MRI images display
- ✅ Charts are interactive

---

### Phase 9: AWS Infrastructure (Week 4)
**Goal:** Create AWS deployment infrastructure

**Deliverables:**
1. AWS CDK project
2. Frontend stack (S3 + CloudFront)
3. Backend stack (Lambda + API Gateway)
4. Database stack (DynamoDB)

**Files to Create:**
```
infrastructure/
├── bin/
│   └── app.ts                     # CDK app entry
├── lib/
│   ├── frontend-stack.ts          # S3 + CloudFront
│   ├── backend-stack.ts           # Lambda + API Gateway
│   └── database-stack.ts          # DynamoDB + S3
├── cdk.json
└── package.json
```

**Success Criteria:**
- ✅ CDK synthesizes successfully
- ✅ Can deploy to AWS
- ✅ All resources created
- ✅ Frontend accessible via URL

---

### Phase 10: Deployment & Testing (Week 4)
**Goal:** Deploy to AWS and test end-to-end

**Deliverables:**
1. Deployed frontend (CloudFront URL)
2. Deployed backend (API Gateway URL)
3. Environment configuration
4. Smoke tests

**Success Criteria:**
- ✅ Frontend loads from CloudFront
- ✅ API calls work
- ✅ Can generate reports
- ✅ Q&A system works
- ✅ All features functional

---

## Step-by-Step Implementation Plan

### Week 1: Backend Foundation
```
Day 1: Setup FastAPI project, health check endpoint
Day 2: Patient endpoints, HealthLake integration
Day 3: Report generation endpoint (basic)
Day 4: Bedrock agent integration
Day 5: S3 storage, async processing
```

### Week 2: Backend Completion + React Start
```
Day 1: Q&A endpoints
Day 2: DynamoDB integration
Day 3: React project setup
Day 4: Layout components
Day 5: Patient selector UI
```

### Week 3: React Features
```
Day 1: Report generator UI
Day 2: Progress indicators
Day 3: Q&A interface
Day 4: Dynamic UI components
Day 5: Visualizations
```

### Week 4: Deployment
```
Day 1: AWS CDK setup
Day 2: Deploy backend
Day 3: Deploy frontend
Day 4: Integration testing
Day 5: Bug fixes, polish
```

---

## Testing Strategy

### Backend Testing
```python
# Test each endpoint
pytest backend/tests/

# Test coverage
pytest --cov=app backend/tests/

# Load testing
locust -f backend/tests/load_test.py
```

### Frontend Testing
```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e

# Build test
npm run build
```

### Integration Testing
- Test frontend → backend communication
- Test AWS services integration
- Test end-to-end workflows

---

## Risk Mitigation

### Risk 1: Backend Timeout
**Problem:** Report generation takes 30-60s
**Solution:** Async processing with job IDs, polling

### Risk 2: CORS Issues
**Problem:** Frontend can't call backend
**Solution:** Configure CORS in FastAPI, API Gateway

### Risk 3: AWS Costs
**Problem:** Unexpected high costs
**Solution:** Set billing alarms, use free tier

### Risk 4: Data Loss
**Problem:** Reports not persisting
**Solution:** S3 storage, DynamoDB backups

### Risk 5: Breaking Changes
**Problem:** New code breaks existing features
**Solution:** Keep Streamlit running, gradual cutover

---

## Success Metrics

### Performance
- ✅ Page load < 2 seconds
- ✅ API response < 500ms (except report generation)
- ✅ Report generation < 60 seconds

### Functionality
- ✅ All Streamlit features replicated
- ✅ No data loss
- ✅ Better UX than Streamlit

### Deployment
- ✅ One-command deployment
- ✅ Auto-scaling works
- ✅ Monitoring in place

---

## Rollback Plan

If migration fails:
1. Keep Streamlit app running
2. Point DNS back to Streamlit
3. Debug React/FastAPI issues
4. Re-deploy when ready

**No downtime approach:**
- Deploy React to new URL first
- Test thoroughly
- Switch DNS when confident
- Keep Streamlit as backup

---

## Documentation Requirements

### API Documentation
- Swagger/OpenAPI (auto-generated)
- Endpoint descriptions
- Request/response examples

### Frontend Documentation
- Component documentation
- State management guide
- Deployment guide

### Infrastructure Documentation
- AWS architecture diagram
- CDK stack documentation
- Cost breakdown

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 5 days | Backend API foundation |
| Phase 2 | 3 days | Report generation API |
| Phase 3 | 2 days | Q&A system API |
| Phase 4 | 3 days | React setup |
| Phase 5 | 3 days | Patient UI |
| Phase 6 | 3 days | Report UI |
| Phase 7 | 3 days | Q&A UI |
| Phase 8 | 2 days | Visualizations |
| Phase 9 | 3 days | AWS infrastructure |
| Phase 10 | 3 days | Deployment & testing |
| **TOTAL** | **30 days** | **Full migration** |

---

## Next Steps

1. ✅ Review this process document
2. ✅ Approve approach
3. ✅ Start Phase 1: Backend API Foundation
4. ✅ Create first endpoint (health check)
5. ✅ Iterate through phases

---

## Questions to Answer Before Starting

1. **Timeline:** Do we have 4 weeks for this migration?
2. **Resources:** Who will work on this? (Frontend dev, backend dev, DevOps)
3. **Priority:** Is this more important than new features?
4. **Budget:** AWS costs acceptable (~$100/month)?
5. **Deployment:** Deploy to production or staging first?

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Today | Migrate to React | Better UX, production-ready |
| Today | Use FastAPI | Keep Python, easy migration |
| Today | Deploy on AWS | Already using Bedrock/HealthLake |
| Today | Use AWS CDK | Infrastructure as code |
| Today | Parallel development | Don't break existing app |

---

## Approval

- [ ] Process document reviewed
- [ ] Timeline approved
- [ ] Budget approved
- [ ] Ready to start Phase 1

**Once approved, we begin with Phase 1, Day 1: FastAPI project setup**
