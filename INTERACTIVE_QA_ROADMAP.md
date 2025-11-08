# Interactive Q&A System - Implementation Roadmap

## Overview
Enable users to ask questions about generated medical reports and receive dynamic UI responses based on cached analysis data.

---

## Phase 1: Foundation (30 mins)

### 1.1 Create Q&A Agent
- **File**: `deploy_qa_agent.py`
- **Action**: Deploy new Bedrock agent specialized for answering questions about cached medical reports
- **Instructions**: `qa_agent_instructions.txt`
- **Capabilities**: 
  - Parse cached report data
  - Identify query intent (risk, comparison, timeline, explanation)
  - Extract relevant information
  - Suggest UI component type
  - Format structured responses

### 1.2 Update Agent Config
- **File**: `agent_config.json`
- **Action**: Add Q&A agent ID and alias

### 1.3 Test Q&A Agent
- **File**: `test_qa_agent.py`
- **Action**: Test with sample cached reports and various question types

**Deliverable**: Working Q&A agent that can answer questions about cached data

---

## Phase 2: Data Caching & Context Management (20 mins)

### 2.1 Create Cache Manager
- **File**: `report_cache_manager.py`
- **Functions**:
  - `cache_comprehensive_report()` - Store all 4 reports in session
  - `get_cached_context()` - Retrieve formatted context for Q&A agent
  - `clear_cache()` - Reset when new patient selected
  - `format_for_qa()` - Structure data for agent consumption

### 2.2 Update Session State
- **File**: `app.py`
- **Action**: Add session state variables:
  - `cached_reports` - All specialist reports
  - `qa_mode` - Boolean for Q&A interface visibility
  - `qa_history` - Conversation history
  - `current_ui_component` - Dynamic UI state

**Deliverable**: Cached report data accessible for Q&A

---

## Phase 3: Q&A Interface Components (40 mins)

### 3.1 Create UI Component Library
- **File**: `qa_ui_components.py`
- **Components**:
  - `render_risk_assessment()` - Risk meters with severity
  - `render_comparison_table()` - Side-by-side specialist comparison
  - `render_timeline()` - Follow-up schedule
  - `render_action_items()` - Prioritized recommendations
  - `render_detailed_card()` - Expandable explanation cards
  - `render_medication_map()` - Drug-condition mapping
  - `render_key_findings()` - Bullet point summaries

### 3.2 Create Query Processor
- **File**: `qa_query_processor.py`
- **Functions**:
  - `process_user_query()` - Send to Q&A agent
  - `parse_agent_response()` - Extract structured data
  - `determine_ui_type()` - Map response to UI component
  - `render_dynamic_ui()` - Call appropriate component renderer

**Deliverable**: Reusable UI components for different query types

---

## Phase 4: UI Integration (30 mins)

### 4.1 Add Q&A Section to App
- **File**: `app.py`
- **Location**: After comprehensive report display
- **Elements**:
  - Collapsible "Ask Questions" section
  - Text input for questions
  - Quick question buttons (Top Risks, Follow-ups, Compare, Medications)
  - Dynamic response area
  - Conversation history

### 4.2 Wire Up Q&A Flow
- **File**: `app.py`
- **Flow**:
  1. User asks question
  2. Get cached reports context
  3. Send to Q&A agent
  4. Parse response
  5. Render appropriate UI component
  6. Add to conversation history

**Deliverable**: Functional Q&A interface in Streamlit app

---

## Phase 5: Enhanced Features (30 mins)

### 5.1 Quick Question Templates
- **File**: `qa_templates.py`
- **Templates**:
  - "What are my top 3 health risks?"
  - "What follow-up appointments do I need?"
  - "Compare findings across specialists"
  - "What medications address my conditions?"
  - "Explain my most concerning finding"
  - "What lifestyle changes are recommended?"

### 5.2 Add Visual Enhancements
- **File**: `qa_ui_components.py`
- **Enhancements**:
  - Color-coded severity (red/yellow/green)
  - Icons for different finding types
  - Progress bars for risk levels
  - Expandable/collapsible sections
  - Source attribution (which specialist)

### 5.3 Context Awareness
- **File**: `qa_query_processor.py`
- **Features**:
  - Maintain conversation context
  - Reference previous questions
  - Follow-up question handling
  - Multi-turn conversations

**Deliverable**: Polished Q&A experience with templates and visuals

---

## Phase 6: Testing & Refinement (20 mins)

### 6.1 Create Test Suite
- **File**: `test_qa_system.py`
- **Tests**:
  - Test all query types
  - Test all UI components
  - Test with different patient data
  - Test conversation flow
  - Test error handling

### 6.2 Create Documentation
- **File**: `QA_SYSTEM_GUIDE.md`
- **Content**:
  - How to use Q&A feature
  - Supported question types
  - UI component examples
  - Architecture overview

**Deliverable**: Tested and documented Q&A system

---

## Implementation Order

```
Phase 1: Foundation
├── deploy_qa_agent.py
├── qa_agent_instructions.txt
├── test_qa_agent.py
└── agent_config.json (update)

Phase 2: Caching
├── report_cache_manager.py
└── app.py (session state updates)

Phase 3: UI Components
├── qa_ui_components.py
└── qa_query_processor.py

Phase 4: Integration
└── app.py (Q&A interface)

Phase 5: Enhancements
├── qa_templates.py
├── qa_ui_components.py (enhancements)
└── qa_query_processor.py (context awareness)

Phase 6: Testing
├── test_qa_system.py
└── QA_SYSTEM_GUIDE.md
```

---

## File Structure

```
HASH5_hackathon/
├── deploy_qa_agent.py              # Deploy Q&A agent
├── qa_agent_instructions.txt       # Agent instructions
├── test_qa_agent.py                # Test Q&A agent
├── report_cache_manager.py         # Cache management
├── qa_ui_components.py             # UI component library
├── qa_query_processor.py           # Query processing logic
├── qa_templates.py                 # Quick question templates
├── test_qa_system.py               # Test suite
├── QA_SYSTEM_GUIDE.md              # Documentation
├── INTERACTIVE_QA_ROADMAP.md       # This file
├── agent_config.json               # Updated with Q&A agent
└── app.py                          # Updated with Q&A interface
```

---

## Technical Decisions

### Agent Strategy: New Specialized Q&A Agent
- **Why**: Clean separation of concerns, optimized for Q&A tasks
- **Alternative**: Could reuse orchestrator but less focused

### UI Approach: Component Library
- **Why**: Reusable, maintainable, extensible
- **Alternative**: Inline rendering but harder to maintain

### Caching Strategy: Session State
- **Why**: Fast, no database needed, automatic cleanup
- **Alternative**: Redis/DynamoDB but overkill for this use case

### Response Format: Structured JSON
- **Why**: Easy to parse, deterministic UI rendering
- **Alternative**: Free text but harder to render dynamically

---

## Success Metrics

- ✅ Q&A agent responds in < 5 seconds
- ✅ Supports 6+ query types
- ✅ 5+ UI component types
- ✅ Maintains conversation context
- ✅ No re-querying HealthLake
- ✅ Works with all patient reports

---

## Timeline

- **Phase 1**: 30 mins
- **Phase 2**: 20 mins
- **Phase 3**: 40 mins
- **Phase 4**: 30 mins
- **Phase 5**: 30 mins
- **Phase 6**: 20 mins

**Total**: ~2.5 hours

---

## Next Steps

1. Review and approve roadmap
2. Start Phase 1: Deploy Q&A agent
3. Iterate through phases sequentially
4. Test after each phase
5. Commit to feature branch
6. Merge to main after full testing
