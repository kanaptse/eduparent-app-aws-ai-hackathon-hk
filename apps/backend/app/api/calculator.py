from fastapi import APIRouter
from app.models.schemas import CalculatorRequest, CalculatorResponse

router = APIRouter()

@router.post("/add", response_model=CalculatorResponse)
async def calculate_sum(request: CalculatorRequest):
    """Add two numbers"""
    result = request.a + request.b
    return CalculatorResponse(result=result)

@router.post("/tuition-estimate")
async def estimate_tuition(
    years: int = 4,
    current_cost: float = 50000.0,
    inflation_rate: float = 0.03
):
    """Estimate future tuition costs (placeholder for real calculator)"""
    future_cost = current_cost * ((1 + inflation_rate) ** years)
    return {
        "current_cost": current_cost,
        "years": years,
        "inflation_rate": inflation_rate,
        "estimated_cost": round(future_cost, 2)
    }