"""Roleplay API endpoints"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.roleplay.services.game_engine import RoleplayGameEngine
from app.roleplay.models.evaluation import EvaluateRequest, GameResponseRequest

router = APIRouter()
game_engine = RoleplayGameEngine()

# In-memory game state storage (in production, use proper session management)
game_sessions: Dict[str, Any] = {}


@router.post("/game/start")
async def start_game(scenario_name: str = None, language: str = "zh-HK"):
    """Start a new game session"""
    try:
        game_state = game_engine.create_game_state(scenario_name, language)

        if not game_state:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Generate session ID (simple implementation)
        session_id = f"session_{len(game_sessions)}"
        game_sessions[session_id] = game_state

        response = {
            "session_id": session_id,
            "scenario": {
                "title": game_state.scenario_title,
                "background": game_state.scenario_background,
                "teen_opening": game_state.teen_opening,
                "is_multi_round": game_state.is_multi_round
            }
        }

        if game_state.is_multi_round:
            response.update({
                "current_round": game_state.current_round,
                "max_rounds": game_state.max_rounds,
                "round_attempts_remaining": game_state.max_round_attempts - game_state.round_attempts
            })
        else:
            response["attempts_remaining"] = game_state.max_attempts - game_state.attempts

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/game/respond/{session_id}")
async def submit_response(session_id: str, request: GameResponseRequest):
    """Submit parent response for evaluation"""

    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")

    game_state = game_sessions[session_id]

    if game_state.game_completed:
        raise HTTPException(status_code=400, detail="Game already completed")

    try:
        # Process the response
        updated_state = await game_engine.process_parent_response(
            game_state,
            request.parent_response
        )

        # Update session
        game_sessions[session_id] = updated_state

        # Build response based on scenario type
        if updated_state.is_multi_round:
            return _build_multi_round_response(updated_state)
        else:
            return _build_single_round_response(updated_state)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _build_single_round_response(game_state):
    """Build response for single-round scenarios"""
    return {
        "evaluation": {
            "tone_score": game_state.evaluation.tone_score,
            "approach_score": game_state.evaluation.approach_score,
            "respect_score": game_state.evaluation.respect_score,
            "total_score": game_state.evaluation.total_score,
            "feedback": game_state.evaluation.feedback,
            "passed": game_state.evaluation.passed
        },
        "teen_response": game_state.teen_response,
        "game_completed": game_state.game_completed,
        "final_score": game_state.final_score,
        "attempts_used": game_state.attempts,
        "attempts_remaining": game_state.max_attempts - game_state.attempts
    }


def _build_multi_round_response(game_state):
    """Build response for multi-round scenarios"""
    response = {
        "is_multi_round": True,
        "current_round": game_state.current_round,
        "max_rounds": game_state.max_rounds,
        "teen_response": game_state.teen_response,
        "round_attempts_used": game_state.round_attempts,
        "round_attempts_remaining": game_state.max_round_attempts - game_state.round_attempts,
        "game_completed": game_state.game_completed
    }

    # Add evaluation if exists
    if game_state.multi_round_evaluation:
        response["evaluation"] = {
            "criteria_scores": game_state.multi_round_evaluation.criteria_scores,
            "total_score": game_state.multi_round_evaluation.total_score,
            "max_possible_score": game_state.multi_round_evaluation.max_possible_score,
            "feedback": game_state.multi_round_evaluation.feedback,
            "detailed_feedback": game_state.multi_round_evaluation.detailed_feedback,
            "passed": game_state.multi_round_evaluation.passed,
            "round_number": game_state.multi_round_evaluation.round_number
        }

    # Add scenario completion if exists
    if game_state.scenario_completion:
        response["scenario_completion"] = {
            "scenario_name": game_state.scenario_completion.scenario_name,
            "rounds_completed": game_state.scenario_completion.rounds_completed,
            "total_rounds": game_state.scenario_completion.total_rounds,
            "rounds_passed": game_state.scenario_completion.rounds_passed,
            "overall_score": game_state.scenario_completion.overall_score,
            "mastery_achieved": game_state.scenario_completion.mastery_achieved,
            "badges_earned": game_state.scenario_completion.badges_earned,
            "communication_techniques_unlocked": game_state.scenario_completion.communication_techniques_unlocked
        }
        response["final_score"] = int(game_state.scenario_completion.overall_score)

    # Add round history summary
    response["rounds_summary"] = [
        {
            "round_number": result.round_number,
            "passed": result.evaluation.passed,
            "score": result.evaluation.total_score,
            "attempts_used": result.attempts_used
        }
        for result in game_state.round_history
    ]

    return response


@router.get("/game/status/{session_id}")
async def get_game_status(session_id: str):
    """Get current game status"""

    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")

    game_state = game_sessions[session_id]

    if game_state.is_multi_round:
        return {
            "session_id": session_id,
            "scenario_title": game_state.scenario_title,
            "is_multi_round": True,
            "current_round": game_state.current_round,
            "max_rounds": game_state.max_rounds,
            "round_attempts_used": game_state.round_attempts,
            "round_attempts_remaining": game_state.max_round_attempts - game_state.round_attempts,
            "game_completed": game_state.game_completed,
            "final_score": game_state.final_score,
            "rounds_completed": len(game_state.round_history),
            "scenario_completion": game_state.scenario_completion.__dict__ if game_state.scenario_completion else None
        }
    else:
        return {
            "session_id": session_id,
            "scenario_title": game_state.scenario_title,
            "is_multi_round": False,
            "attempts_used": game_state.attempts,
            "attempts_remaining": game_state.max_attempts - game_state.attempts,
            "game_completed": game_state.game_completed,
            "final_score": game_state.final_score
        }


@router.get("/game/round-status/{session_id}")
async def get_round_status(session_id: str):
    """Get detailed round status for multi-round games"""

    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")

    game_state = game_sessions[session_id]

    if not game_state.is_multi_round:
        raise HTTPException(status_code=400, detail="Not a multi-round game")

    return {
        "session_id": session_id,
        "scenario_title": game_state.scenario_title,
        "current_round": game_state.current_round,
        "max_rounds": game_state.max_rounds,
        "round_attempts_used": game_state.round_attempts,
        "round_attempts_remaining": game_state.max_round_attempts - game_state.round_attempts,
        "round_history": [
            {
                "round_number": result.round_number,
                "parent_response": result.parent_response,
                "child_response": result.child_response,
                "evaluation": {
                    "criteria_scores": result.evaluation.criteria_scores,
                    "total_score": result.evaluation.total_score,
                    "max_possible_score": result.evaluation.max_possible_score,
                    "feedback": result.evaluation.feedback,
                    "passed": result.evaluation.passed
                },
                "attempts_used": result.attempts_used,
                "completed_at": result.completed_at
            }
            for result in game_state.round_history
        ],
        "current_evaluation": game_state.multi_round_evaluation.__dict__ if game_state.multi_round_evaluation else None,
        "scenario_completion": game_state.scenario_completion.__dict__ if game_state.scenario_completion else None
    }


@router.delete("/game/end/{session_id}")
async def end_game(session_id: str):
    """End a game session"""

    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")

    del game_sessions[session_id]

    return {"message": "Game session ended"}


@router.get("/scenarios/")
async def list_scenarios():
    """List available scenarios"""
    try:
        scenarios = game_engine.get_available_scenarios()
        return {"scenarios": scenarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/{scenario_name}")
async def get_scenario(scenario_name: str, language: str = "zh-HK"):
    """Get a specific scenario"""
    try:
        scenario = game_engine.get_scenario(scenario_name)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        return {
            "title": scenario.get_title(language),
            "background": scenario.get_background(language),
            "teen_opening": scenario.get_teen_opening(language),
            "level": scenario.level,
            "is_multi_round": scenario.is_multi_round
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))