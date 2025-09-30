from fastapi import APIRouter
from app.models.schemas import SurveyRequest, SurveyResponse
from app.services.survey_service import generate_report

router = APIRouter()

@router.post("/submit", response_model=SurveyResponse)
async def submit_survey(request: SurveyRequest):
    """Submit survey and get personalized report"""
    return await generate_report(request)

@router.get("/goals")
async def get_available_goals():
    """Get list of available goals"""
    return {
        "goals": [
            "Improve study habits",
            "Strengthen parent–child relationship", 
            "Explore extracurriculars",
            "Plan university pathway"
        ]
    }