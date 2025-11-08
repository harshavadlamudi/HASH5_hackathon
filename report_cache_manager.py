import json

def cache_comprehensive_report(session_state, cardiology, radiology, endocrinology, comprehensive, patient_summary):
    """Cache all specialist reports in session state"""
    session_state['cached_reports'] = {
        'cardiology': cardiology,
        'radiology': radiology,
        'endocrinology': endocrinology,
        'comprehensive': comprehensive,
        'patient_summary': patient_summary
    }

def get_cached_context(session_state):
    """Get formatted context for Q&A agent"""
    if 'cached_reports' not in session_state:
        return None
    
    reports = session_state['cached_reports']
    summary = reports['patient_summary']
    
    context = f"""
PATIENT INFORMATION:
Name: {summary.get('name', 'Unknown')}
Gender: {summary.get('gender', 'Unknown')}
Birth Date: {summary.get('birthDate', 'Unknown')}

CARDIOLOGY REPORT:
{reports['cardiology']}

RADIOLOGY REPORT:
{reports['radiology']}

ENDOCRINOLOGY REPORT:
{reports['endocrinology']}

COMPREHENSIVE ANALYSIS:
{reports['comprehensive']}
"""
    return context

def clear_cache(session_state):
    """Clear cached reports"""
    if 'cached_reports' in session_state:
        del session_state['cached_reports']
    if 'qa_history' in session_state:
        del session_state['qa_history']

def has_cached_reports(session_state):
    """Check if reports are cached"""
    return 'cached_reports' in session_state and session_state['cached_reports'] is not None
