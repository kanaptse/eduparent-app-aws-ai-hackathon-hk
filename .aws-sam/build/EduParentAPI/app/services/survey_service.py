from app.models.schemas import SurveyRequest, SurveyResponse


def get_recommendation(goal: str) -> str:
    """Get recommendation based on selected communication goal"""
    recommendations = {
        "Improve emotional connection": "Practice emotion labeling: When your child shows emotion, try 'You seem [frustrated/excited/disappointed]. Is that what you're feeling?' This validates their experience and builds emotional intelligence.",
        "Reduce daily conflicts": "Use collaborative language: Replace 'You need to...' with 'How can we solve this together?' This shifts from power struggle to partnership and reduces resistance.",
        "Better understand my child's development": "Learn age-appropriate expectations: A 7-year-old processes emotions differently than a 14-year-old. Adjust your communication style to match their developmental stage for better connection.",
        "Handle emotional outbursts": "Practice the 6-second rule: When triggers arise, wait 6 seconds before responding. This allows neurochemical floods to recede and prevents reactive communication patterns."
    }
    return recommendations.get(goal, "Focus on one communication technique this week: validate feelings before problem-solving. Notice how your child responds differently.")


def get_tiny_actions() -> list[str]:
    """Get list of tiny communication actions for this week"""
    return [
        "Practice one emotion labeling phrase: 'You seem [emotion]. Is that what you're feeling?'",
        "Set a daily 5-minute device-free conversation time with your child.",
        "Notice your emotional triggers and take 6 seconds before responding.",
        "Ask one open-ended question daily: 'What was interesting about your day?'",
        "Review weekly: Which communication technique felt most natural? What did you notice about your child's responses?"
    ]


async def generate_report(request: SurveyRequest) -> SurveyResponse:
    """Generate personalized report based on survey responses"""
    recommendation = get_recommendation(request.goal)
    tiny_actions = get_tiny_actions()
    
    return SurveyResponse(
        goal=request.goal,
        note=request.note or "",
        recommendation=recommendation,
        tiny_actions=tiny_actions
    )