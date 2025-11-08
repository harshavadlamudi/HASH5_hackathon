import streamlit as st

def render_risk_assessment(data):
    """Render risk assessment with severity indicators"""
    st.markdown("### Health Risk Assessment")
    
    for risk in data.get('risks', []):
        level = risk['level'].lower()
        color = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(level, '⚪')
        
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"## {color}")
            with col2:
                st.markdown(f"**{risk['name']}** - {level.upper()}")
                st.caption(risk['description'])
            st.divider()

def render_comparison_table(data):
    """Render side-by-side specialist comparison"""
    st.markdown("### Specialist Comparison")
    
    specialists = data.get('specialists', [])
    findings = data.get('findings', [])
    
    if len(specialists) >= 2:
        for finding in findings:
            st.markdown(f"**{finding['aspect']}**")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**{specialists[0].title()}**\n\n{finding.get('specialist1', 'N/A')}")
            with col2:
                st.info(f"**{specialists[1].title()}**\n\n{finding.get('specialist2', 'N/A')}")
            st.divider()

def render_timeline(data):
    """Render follow-up timeline"""
    st.markdown("### Follow-up Schedule")
    
    appointments = data.get('appointments', [])
    
    for apt in appointments:
        priority = apt.get('priority', 'medium').lower()
        icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
        
        with st.expander(f"{icon} {apt['type']} - {apt['timeframe']}"):
            st.markdown(f"**Priority:** {priority.upper()}")
            st.markdown(f"**Reason:** {apt['reason']}")

def render_action_items(data):
    """Render prioritized action items"""
    st.markdown("### Action Plan")
    
    actions = sorted(data.get('actions', []), key=lambda x: x.get('priority', 999))
    
    for action in actions:
        urgency = action.get('urgency', 'routine').lower()
        color = {'immediate': 'error', 'soon': 'warning', 'routine': 'info'}.get(urgency, 'info')
        
        with st.container():
            getattr(st, color)(f"**{action['priority']}. {action['action']}**")
            st.caption(f"Urgency: {urgency.upper()} | Recommended by: {action.get('specialist', 'N/A')}")
            st.divider()

def render_detailed_card(data):
    """Render detailed explanation card"""
    st.markdown(f"### {data.get('title', 'Details')}")
    
    st.info(data.get('summary', ''))
    
    if data.get('details'):
        with st.expander("More Details"):
            for detail in data['details']:
                st.markdown(f"- {detail}")
    
    if data.get('implications'):
        st.warning(f"**Implications:** {data['implications']}")

def render_key_findings(data):
    """Render key findings summary"""
    st.markdown("### Key Findings")
    
    findings = data.get('findings', [])
    
    for finding in findings:
        with st.container():
            st.markdown(f"**{finding['category']}**")
            st.write(finding['finding'])
            st.caption(f"Significance: {finding['significance']}")
            st.divider()

def render_medication_map(data):
    """Render medication-condition mapping"""
    st.markdown("### Medication Overview")
    
    medications = data.get('medications', [])
    
    for med in medications:
        with st.expander(f"💊 {med['drug']}"):
            st.markdown(f"**Treats:** {', '.join(med.get('conditions', []))}")
            st.caption(f"Prescribed by: {med.get('specialist', 'N/A')}")

def render_dynamic_response(ui_type, data):
    """Route to appropriate UI component"""
    renderers = {
        'risk_assessment': render_risk_assessment,
        'comparison': render_comparison_table,
        'timeline': render_timeline,
        'action_items': render_action_items,
        'detailed_card': render_detailed_card,
        'key_findings': render_key_findings,
        'medication_map': render_medication_map
    }
    
    renderer = renderers.get(ui_type)
    if renderer:
        renderer(data)
    else:
        st.warning(f"Unknown UI type: {ui_type}")
