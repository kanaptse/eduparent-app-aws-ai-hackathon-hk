"""YAML scenario loading and management"""

import os
import yaml
from typing import List, Optional
from pydantic import BaseModel
from ..config import GameConfig


class RoundData(BaseModel):
    """Data for a single round in multi-round scenario"""

    round: int
    child_state: str
    child_prompt: str
    child_prompt_zh: Optional[str] = None
    evaluation_criteria: List[str]
    pass_threshold: int = 7

    def get_child_prompt(self, language: str = "en") -> str:
        """Get child prompt in specified language"""
        if language == "zh-HK" and self.child_prompt_zh:
            return self.child_prompt_zh
        return self.child_prompt


class Scenario(BaseModel):
    """A roleplay scenario"""

    case_name: str
    case_name_zh: Optional[str] = None
    background_and_instructions: str
    background_and_instructions_zh: Optional[str] = None
    child_prompts: List[str] = []  # Legacy field for single-round scenarios

    # Multi-round scenario fields
    multi_round: bool = False
    rounds: Optional[List[RoundData]] = None

    def get_title(self, language: str = "en") -> str:
        """Get scenario title in specified language"""
        if language == "zh-HK" and self.case_name_zh:
            return self.case_name_zh
        return self.case_name

    def get_background(self, language: str = "en") -> str:
        """Get background description in specified language"""
        if language == "zh-HK" and self.background_and_instructions_zh:
            return self.background_and_instructions_zh
        return self.background_and_instructions

    @property
    def title(self) -> str:
        """Get scenario title"""
        return self.case_name

    @property
    def background(self) -> str:
        """Get background description"""
        return self.background_and_instructions

    def get_teen_opening(self, language: str = "en") -> str:
        """Get the teen's opening line (first prompt) in specified language"""
        if self.multi_round and self.rounds:
            return self.rounds[0].get_child_prompt(language)

        # For single-round scenarios, pick the appropriate language prompt
        if not self.child_prompts:
            return ""

        if language == "zh-HK" and len(self.child_prompts) > 1:
            # Return second prompt (Cantonese) if available
            return self.child_prompts[1]

        # Return first prompt (English) by default
        return self.child_prompts[0]

    @property
    def teen_opening(self) -> str:
        """Get the teen's opening line (first prompt) - legacy property"""
        return self.get_teen_opening("en")

    @property
    def level(self) -> int:
        """Get scenario level based on number of prompts/rounds"""
        if self.multi_round and self.rounds:
            return len(self.rounds)
        return len(self.child_prompts)

    @property
    def is_multi_round(self) -> bool:
        """Check if this is a multi-round scenario"""
        return self.multi_round and self.rounds is not None

    @property
    def max_rounds(self) -> int:
        """Get maximum number of rounds"""
        if self.is_multi_round:
            return len(self.rounds)
        return 1

    def get_round_data(self, round_number: int) -> Optional[RoundData]:
        """Get data for a specific round (1-indexed)"""
        if not self.is_multi_round or not self.rounds:
            return None

        # Convert to 0-indexed
        round_index = round_number - 1
        if 0 <= round_index < len(self.rounds):
            return self.rounds[round_index]
        return None

    def get_evaluation_criteria(self, round_number: int) -> List[str]:
        """Get evaluation criteria for a specific round"""
        round_data = self.get_round_data(round_number)
        if round_data:
            return round_data.evaluation_criteria
        return ["tone_score", "approach_score", "respect_score"]  # Default criteria

    def get_pass_threshold(self, round_number: int) -> int:
        """Get pass threshold for a specific round"""
        round_data = self.get_round_data(round_number)
        if round_data:
            return round_data.pass_threshold
        return 7  # Default threshold


class ScenarioLoader:
    """Loader for YAML scenario files"""

    def __init__(self, scenarios_dir: Optional[str] = None):
        self.scenarios_dir = scenarios_dir or GameConfig.SCENARIOS_DIR

    def load_scenario(self, scenario_name: str) -> Optional[Scenario]:
        """Load a specific scenario by name"""
        scenario_path = os.path.join(self.scenarios_dir, f"{scenario_name}.yaml")

        if not os.path.exists(scenario_path):
            return None

        try:
            with open(scenario_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            return Scenario(**data)

        except Exception as e:
            print(f"Error loading scenario {scenario_name}: {e}")
            return None

    def list_scenarios(self) -> List[str]:
        """List all available scenario names"""
        if not os.path.exists(self.scenarios_dir):
            return []

        scenarios = []
        for filename in os.listdir(self.scenarios_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                scenario_name = os.path.splitext(filename)[0]
                # Temporarily hide school_dropoff_anxiety scenario
                if scenario_name != "school_dropoff_anxiety":
                    scenarios.append(scenario_name)

        return sorted(scenarios)

    def load_all_scenarios(self) -> List[Scenario]:
        """Load all available scenarios"""
        scenarios = []
        for scenario_name in self.list_scenarios():
            scenario = self.load_scenario(scenario_name)
            if scenario:
                scenarios.append(scenario)

        return scenarios

    def get_default_scenario(self) -> Optional[Scenario]:
        """Get the default scenario (first available)"""
        scenario_names = self.list_scenarios()
        if scenario_names:
            return self.load_scenario(scenario_names[0])
        return None