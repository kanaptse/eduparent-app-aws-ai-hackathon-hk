"""Game state management"""

from typing import Optional, List
from pydantic import BaseModel


class GameState(BaseModel):
    """State tracking for the roleplay game"""

    # Scenario information
    scenario_title: str
    scenario_background: str
    teen_opening: str
    is_multi_round: bool = False
    language: str = "zh-HK"  # User's preferred language

    # Single-round game progress (legacy)
    parent_response: str = ""
    attempts: int = 0
    max_attempts: int = 3

    # Multi-round game progress
    current_round: int = 1
    max_rounds: int = 3
    round_attempts: int = 0  # Attempts for current round
    max_round_attempts: int = 3
    round_history: List['RoundResult'] = []

    # Results
    evaluation: Optional['EvaluationResult'] = None
    multi_round_evaluation: Optional['MultiRoundEvaluationResult'] = None
    teen_response: Optional[str] = None
    game_completed: bool = False
    final_score: Optional[int] = None
    scenario_completion: Optional['ScenarioCompletion'] = None

    def can_retry(self) -> bool:
        """Check if player can make another attempt"""
        if self.is_multi_round:
            return self.round_attempts < self.max_round_attempts and not self.game_completed
        return self.attempts < self.max_attempts and not self.game_completed

    def is_passed(self) -> bool:
        """Check if the current attempt passed"""
        if self.is_multi_round:
            return self.multi_round_evaluation is not None and self.multi_round_evaluation.passed
        return self.evaluation is not None and self.evaluation.passed

    def increment_attempt(self) -> None:
        """Increment the attempt counter"""
        if self.is_multi_round:
            self.round_attempts += 1
        else:
            self.attempts += 1

    def advance_to_next_round(self) -> None:
        """Advance to the next round"""
        if self.is_multi_round and self.current_round < self.max_rounds:
            self.current_round += 1
            self.round_attempts = 0
            self.parent_response = ""
            self.teen_response = None
            self.multi_round_evaluation = None

    def can_advance_round(self) -> bool:
        """Check if can advance to next round"""
        return (self.is_multi_round and
                self.current_round < self.max_rounds and
                (self.is_passed() or self.round_attempts >= self.max_round_attempts))

    def is_scenario_complete(self) -> bool:
        """Check if entire scenario is complete"""
        if self.is_multi_round:
            return self.current_round >= self.max_rounds or self.game_completed
        return self.game_completed

    def complete_game(self, final_score: Optional[int] = None) -> None:
        """Mark the game as completed"""
        self.game_completed = True
        self.final_score = final_score

    def get_current_round_prompt(self, scenario: 'Scenario') -> str:
        """Get the current round's prompt for multi-round scenarios"""
        if not self.is_multi_round or not hasattr(scenario, 'rounds'):
            return scenario.teen_opening

        round_data = scenario.get_round_data(self.current_round)
        return round_data.get('child_prompt', scenario.teen_opening) if round_data else scenario.teen_opening


# Forward reference resolution
from .evaluation import EvaluationResult, MultiRoundEvaluationResult, RoundResult, ScenarioCompletion
GameState.model_rebuild()