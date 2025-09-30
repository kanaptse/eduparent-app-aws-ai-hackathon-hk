"""Core game engine for roleplay scenarios"""

from typing import Optional
from ..models.game_state import GameState
from ..models.evaluation import EvaluationResult, RoundResult
from ..agents.evaluator import EvaluationAgent
from ..agents.teen_responder import TeenResponderAgent
from ..scenarios.loader import ScenarioLoader, Scenario
from ..config import GameConfig


class RoleplayGameEngine:
    """Core game engine managing the roleplay flow"""

    def __init__(self):
        self.evaluator = EvaluationAgent()
        self.teen_responder = TeenResponderAgent()
        self.scenario_loader = ScenarioLoader()

    def create_game_state(self, scenario_name: Optional[str] = None, language: str = "zh-HK") -> Optional[GameState]:
        """Create a new game state with the specified scenario"""

        # Load scenario
        if scenario_name:
            scenario = self.scenario_loader.load_scenario(scenario_name)
        else:
            scenario = self.scenario_loader.get_default_scenario()

        if not scenario:
            return None

        # Create game state with multi-round support
        game_state = GameState(
            scenario_title=scenario.get_title(language),
            scenario_background=scenario.get_background(language),
            teen_opening=scenario.get_teen_opening(language),
            max_attempts=GameConfig.MAX_ATTEMPTS,
            is_multi_round=scenario.is_multi_round,
            max_rounds=scenario.max_rounds if scenario.is_multi_round else 1,
            language=language
        )

        return game_state

    async def process_parent_response(self, game_state: GameState, parent_response: str) -> GameState:
        """Process a parent's response and update game state"""

        # Update game state with parent response
        game_state.parent_response = parent_response
        game_state.increment_attempt()

        # Get current scenario for context
        # Try to map scenario title to filename
        scenario_name = None
        if "school drop" in game_state.scenario_title.lower():
            scenario_name = "school_dropoff_anxiety"
        elif "messy" in game_state.scenario_title.lower():
            scenario_name = "messy_room"
        else:
            # Fallback to the title-based conversion
            scenario_name = game_state.scenario_title.replace(" ", "_").lower().replace("-", "_")

        scenario = self.scenario_loader.load_scenario(scenario_name)
        if not scenario:
            # Fallback to default evaluation
            return await self._process_single_round_response(game_state, parent_response)

        if game_state.is_multi_round:
            return await self._process_multi_round_response(game_state, parent_response, scenario)
        else:
            return await self._process_single_round_response(game_state, parent_response)

    async def _process_single_round_response(self, game_state: GameState, parent_response: str) -> GameState:
        """Process response for single-round scenarios (legacy)"""

        # Evaluate the response with language support
        evaluation = await self.evaluator.evaluate(
            parent_response,
            game_state.teen_opening,
            language=game_state.language
        )
        game_state.evaluation = evaluation

        # Generate teen response with language support
        teen_response = await self.teen_responder.respond(
            evaluation.total_score,
            context=game_state.scenario_background,
            language=game_state.language
        )
        game_state.teen_response = teen_response.response

        # Check if game should end
        if evaluation.passed:
            game_state.complete_game(evaluation.total_score)
        elif not game_state.can_retry():
            game_state.complete_game()

        return game_state

    async def _process_multi_round_response(self, game_state: GameState, parent_response: str, scenario: 'Scenario') -> GameState:
        """Process response for multi-round scenarios"""

        # Get current round data
        round_data = scenario.get_round_data(game_state.current_round)
        if not round_data:
            return game_state

        # Evaluate the response with round-specific criteria and language support
        evaluation = await self.evaluator.evaluate_multi_round(
            parent_response,
            round_data.child_prompt,
            round_data.evaluation_criteria,
            round_data.pass_threshold,
            game_state.current_round,
            language=game_state.language
        )
        game_state.multi_round_evaluation = evaluation

        # Generate teen response with language support
        teen_response = await self.teen_responder.respond(
            evaluation.total_score,
            context=f"{game_state.scenario_background} Child state: {round_data.child_state}",
            language=game_state.language
        )
        game_state.teen_response = teen_response.response

        # Handle round completion/advancement
        if evaluation.passed or game_state.round_attempts >= game_state.max_round_attempts:
            # Save round result
            from datetime import datetime
            round_result = RoundResult(
                round_number=game_state.current_round,
                parent_response=parent_response,
                child_response=teen_response.response,
                evaluation=evaluation,
                attempts_used=game_state.round_attempts,
                completed_at=datetime.now().isoformat()
            )
            game_state.round_history.append(round_result)

            # Check if we can advance or complete
            if game_state.current_round >= game_state.max_rounds:
                # Scenario complete
                completion = self._create_scenario_completion(game_state, scenario)
                game_state.scenario_completion = completion
                game_state.complete_game(int(completion.overall_score))
            else:
                # Advance to next round
                game_state.advance_to_next_round()

        return game_state

    def _create_scenario_completion(self, game_state: GameState, scenario: 'Scenario') -> 'ScenarioCompletion':
        """Create scenario completion result"""
        from .evaluation import ScenarioCompletion

        rounds_passed = sum(1 for result in game_state.round_history if result.evaluation.passed)
        total_score = sum(result.evaluation.total_score for result in game_state.round_history if result.evaluation.passed)
        avg_score = total_score / rounds_passed if rounds_passed > 0 else 0

        badges = []
        techniques = []

        if rounds_passed == game_state.max_rounds:
            badges.append("scenario_mastery")
            techniques.append("separation_anxiety_management")

        if avg_score >= 9:
            badges.append("expert_communicator")

        return ScenarioCompletion(
            scenario_name=scenario.title,
            rounds_completed=len(game_state.round_history),
            total_rounds=game_state.max_rounds,
            rounds_passed=rounds_passed,
            overall_score=avg_score,
            mastery_achieved=rounds_passed == game_state.max_rounds,
            badges_earned=badges,
            communication_techniques_unlocked=techniques
        )

    async def advance_to_next_round(self, game_state: GameState) -> GameState:
        """Manually advance to next round (for API endpoint)"""
        if game_state.can_advance_round():
            # Get scenario to update teen opening using the same mapping logic
            scenario_name = None
            if "school drop" in game_state.scenario_title.lower():
                scenario_name = "school_dropoff_anxiety"
            elif "messy" in game_state.scenario_title.lower():
                scenario_name = "messy_room"
            else:
                scenario_name = game_state.scenario_title.replace(" ", "_").lower().replace("-", "_")

            scenario = self.scenario_loader.load_scenario(scenario_name)
            if scenario:
                game_state.advance_to_next_round()
                # Update teen opening for new round
                round_data = scenario.get_round_data(game_state.current_round)
                if round_data:
                    game_state.teen_opening = round_data.child_prompt

        return game_state

    def get_available_scenarios(self) -> list[str]:
        """Get list of available scenario names"""
        return self.scenario_loader.list_scenarios()

    def get_scenario(self, scenario_name: str) -> Optional[Scenario]:
        """Get a specific scenario"""
        return self.scenario_loader.load_scenario(scenario_name)