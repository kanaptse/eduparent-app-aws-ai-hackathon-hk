"""Evaluation and response models"""

from pydantic import BaseModel
from typing import Dict, List, Optional


class EvaluationResult(BaseModel):
    """Result of evaluating a parent's response"""

    # Scoring breakdown
    tone_score: int  # 0-4
    approach_score: int  # 0-3
    respect_score: int  # 0-3
    total_score: int  # 0-10

    # Feedback and result
    feedback: str
    passed: bool  # True if score >= threshold

    @classmethod
    def from_dict(cls, data: dict) -> 'EvaluationResult':
        """Create from dictionary (e.g., from AI response JSON)"""
        return cls(
            tone_score=data['tone_score'],
            approach_score=data['approach_score'],
            respect_score=data['respect_score'],
            total_score=data['total_score'],
            feedback=data['feedback'],
            passed=data['passed']
        )


class MultiRoundEvaluationResult(BaseModel):
    """Result for multi-round scenario evaluation with dynamic criteria"""

    # Dynamic scoring based on round criteria
    criteria_scores: Dict[str, int]  # e.g., {"emotion_acknowledgment": 3, "tone_empathy": 2}
    total_score: int
    max_possible_score: int

    # Feedback and result
    feedback: str
    detailed_feedback: Dict[str, str]  # Per-criterion feedback
    passed: bool
    round_number: int

    @classmethod
    def from_dict(cls, data: dict, round_number: int) -> 'MultiRoundEvaluationResult':
        """Create from dictionary with round context"""
        return cls(
            criteria_scores=data.get('criteria_scores', {}),
            total_score=data['total_score'],
            max_possible_score=data.get('max_possible_score', 10),
            feedback=data['feedback'],
            detailed_feedback=data.get('detailed_feedback', {}),
            passed=data['passed'],
            round_number=round_number
        )


class RoundResult(BaseModel):
    """Result of a completed round"""

    round_number: int
    parent_response: str
    child_response: str
    evaluation: MultiRoundEvaluationResult
    attempts_used: int
    completed_at: Optional[str] = None  # ISO timestamp


class ScenarioCompletion(BaseModel):
    """Overall scenario completion result"""

    scenario_name: str
    rounds_completed: int
    total_rounds: int
    rounds_passed: int
    overall_score: float  # Average of all passed rounds
    mastery_achieved: bool  # True if all rounds passed
    badges_earned: List[str] = []
    communication_techniques_unlocked: List[str] = []


class TeenResponse(BaseModel):
    """Teen's response based on evaluation"""

    response: str
    emotion: str  # cooperative, reluctant, defensive, upset

    @classmethod
    def from_dict(cls, data: dict) -> 'TeenResponse':
        """Create from dictionary (e.g., from AI response JSON)"""
        return cls(
            response=data['response'],
            emotion=data.get('emotion', 'neutral')
        )


# API Request/Response models
class EvaluateRequest(BaseModel):
    """Request to evaluate parent response (standalone evaluation)"""
    parent_response: str
    teen_opening: str
    language: Optional[str] = "zh-HK"  # Default to Cantonese for backward compatibility


class GameResponseRequest(BaseModel):
    """Request to submit parent response in game"""
    parent_response: str


class TeenResponseRequest(BaseModel):
    """Request for teen response"""
    score: int
    context: str = ""  # Optional context for better responses