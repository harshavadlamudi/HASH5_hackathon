"""Quick question templates for common queries"""

QUICK_QUESTIONS = [
    {
        'label': '🎯 Top Risks',
        'question': 'What are my top 3 health risks?'
    },
    {
        'label': '📅 Follow-ups',
        'question': 'What follow-up appointments do I need?'
    },
    {
        'label': '🔄 Compare',
        'question': 'Compare findings across all specialists'
    },
    {
        'label': '💊 Medications',
        'question': 'What medications address my conditions?'
    },
    {
        'label': '⚠️ Most Concerning',
        'question': 'Explain my most concerning finding'
    },
    {
        'label': '✅ Action Plan',
        'question': 'What should I do first?'
    }
]

def get_quick_questions():
    """Return list of quick question templates"""
    return QUICK_QUESTIONS
