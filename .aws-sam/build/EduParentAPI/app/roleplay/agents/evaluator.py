"""Parent response evaluation agent"""

import json
import logging
from typing import Optional, List
from pydantic_ai import Agent
from ..config import ModelConfig
from ..models.evaluation import EvaluationResult, MultiRoundEvaluationResult

logger = logging.getLogger(__name__)


class EvaluationAgent:
    """Agent responsible for evaluating parent responses"""

    def __init__(self):
        self._agent = Agent(ModelConfig.get_evaluation_model())
        self._multi_round_agent = Agent(ModelConfig.get_evaluation_model())
        self._setup_system_prompt()
        self._setup_multi_round_prompt()

    def _setup_system_prompt(self):
        """Configure the evaluation system prompt"""
        @self._agent.system_prompt
        def evaluation_prompt() -> str:
            return """You are evaluating parent-teen communication quality on a 0-10 scale.

IMPORTANT: You MUST provide feedback in the language requested by the user.
- If language is "en", provide ALL feedback in English only
- If language is "zh-HK", provide ALL feedback in Cantonese only

RUBRIC:
- Tone (0-4): 4=Very calm/patient, 3=Mostly calm, 2=Neutral, 1=Slightly frustrated, 0=Angry/harsh
- Approach (0-3): 3=Solution-focused/collaborative, 2=Clear expectations with reasoning, 1=Direct instruction, 0=Dismissive/demanding
- Respect (0-3): 3=Acknowledges teen feelings, 2=Shows understanding, 1=Neutral, 0=Ignores/dismisses feelings

Return your evaluation as a JSON object with:
- tone_score: int (0-4)
- approach_score: int (0-3)
- respect_score: int (0-3)
- total_score: int (sum of above, 0-10)
- feedback: str (in the requested language)
- passed: bool (true if total_score >= 7)

Be strict but fair in scoring. Provide specific feedback in the requested language exactly."""

    def _setup_multi_round_prompt(self):
        """Configure the multi-round evaluation system prompt"""
        @self._multi_round_agent.system_prompt
        def multi_round_evaluation_prompt() -> str:
            return """You are evaluating parent communication in a multi-round scenario with dynamic criteria.

IMPORTANT: You MUST provide feedback in the language requested by the user.
- If language is "en", provide ALL feedback in English only
- If language is "zh-HK", provide ALL feedback in Cantonese only

EVALUATION CRITERIA (varies by round):

ROUND 1 - Initial Resistance:
- emotion_acknowledgment (0-3): Recognizes and validates child's emotions
- tone_empathy (0-2): Uses calm, empathetic tone
- solution_approach (0-3): Offers helpful, collaborative solutions

ROUND 2 - Deeper Fear Expression:
- fear_validation (0-4): Acknowledges and validates specific fears
- concrete_reassurance (0-3): Provides specific, tangible reassurance
- collaborative_approach (0-3): Involves child in problem-solving

ROUND 3 - Transition Challenge:
- transition_strategy (0-4): Uses effective transition techniques
- child_agency (0-3): Empowers child with choices/control
- follow_through_clarity (0-3): Provides clear, consistent expectations

Return evaluation as JSON:
- criteria_scores: dict with each criterion and score
- total_score: int (sum of all criteria scores)
- max_possible_score: int (maximum possible for this round)
- feedback: str (overall feedback in the requested language)
- detailed_feedback: dict with feedback for each criterion in the requested language
- passed: bool (true if total_score >= threshold)

Be specific in feedback. Focus on what worked and what could improve. Remember to match the requested language exactly."""

    async def evaluate(self, parent_response: str, teen_opening: str, language: str = "zh-HK") -> EvaluationResult:
        """Evaluate a parent's response"""

        if language == "en":
            prompt = f"""Evaluate this parent's response to a teenager: '{parent_response}'

Situation: The teenager said: "{teen_opening}"
LANGUAGE: English - ALL feedback must be in English only!

Please rate according to tone, approach, and respect criteria. Return pure JSON format only, no other text."""
        else:
            prompt = f"""評估呢個父母對青少年嘅回應：'{parent_response}'

情境：青少年話「{teen_opening}」
語言：廣東話 - 所有反饋必須只用廣東話！

請根據語調、方法、尊重三個標準評分。返回純JSON格式，唔好其他文字。"""

        try:
            logger.info(f"Starting evaluation with model: {ModelConfig.get_evaluation_model()}, language: {language}")
            result = await self._agent.run(prompt)
            logger.info(f"Raw AI response: {result.output}")

            # Clean up response (remove markdown formatting)
            output = self._clean_json_output(result.output)
            logger.info(f"Cleaned JSON output: {output}")

            # Parse JSON
            eval_data = json.loads(output)

            return EvaluationResult.from_dict(eval_data)

        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            # Fallback evaluation on error
            return self._create_fallback_evaluation(str(e), language)

    def _clean_json_output(self, output: str) -> str:
        """Clean up JSON output from AI response"""
        output = output.strip()
        if output.startswith('```json'):
            output = output[7:]
        if output.endswith('```'):
            output = output[:-3]
        return output.strip()

    def _create_fallback_evaluation(self, error: str, language: str = "zh-HK") -> EvaluationResult:
        """Create fallback evaluation when AI fails"""
        if language == "en":
            feedback = f"Evaluation system error, please retry. Error: {error}"
        else:
            feedback = f"評估系統出現錯誤，請重試。錯誤：{error}"

        return EvaluationResult(
            tone_score=2,
            approach_score=2,
            respect_score=2,
            total_score=6,
            feedback=feedback,
            passed=False
        )

    async def evaluate_multi_round(
        self,
        parent_response: str,
        child_prompt: str,
        criteria: List[str],
        threshold: int,
        round_number: int,
        language: str = "zh-HK"
    ) -> MultiRoundEvaluationResult:
        """Evaluate a parent's response for multi-round scenarios"""

        # Build criteria description
        criteria_desc = ", ".join(criteria)

        if language == "en":
            prompt = f"""Evaluate Round {round_number} parent's response to child: '{parent_response}'

Child said: '{child_prompt}'

Evaluation criteria: {criteria_desc}
Passing score: {threshold}
LANGUAGE: English - ALL feedback must be in English only!

Please rate according to Round {round_number} criteria. Return pure JSON format only, no other text."""
        else:
            prompt = f"""評估第{round_number}輪父母對子女嘅回應：'{parent_response}'

子女話：'{child_prompt}'

評估標準：{criteria_desc}
合格分數：{threshold}
語言：廣東話 - 所有反饋必須只用廣東話！

請根據第{round_number}輪嘅標準評分。返回純JSON格式，唔好其他文字。"""

        try:
            logger.info(f"Starting multi-round evaluation for round {round_number}")
            result = await self._multi_round_agent.run(prompt)
            logger.info(f"Raw AI response: {result.output}")

            # Clean up response
            output = self._clean_json_output(result.output)
            logger.info(f"Cleaned JSON output: {output}")

            # Parse JSON
            eval_data = json.loads(output)

            # Calculate max possible score based on criteria
            max_scores = {
                "emotion_acknowledgment": 3, "tone_empathy": 2, "solution_approach": 3,
                "fear_validation": 4, "concrete_reassurance": 3, "collaborative_approach": 3,
                "transition_strategy": 4, "child_agency": 3, "follow_through_clarity": 3
            }

            max_possible = sum(max_scores.get(criterion, 3) for criterion in criteria)
            eval_data["max_possible_score"] = max_possible

            # Ensure passed is calculated correctly
            eval_data["passed"] = eval_data.get("total_score", 0) >= threshold

            return MultiRoundEvaluationResult.from_dict(eval_data, round_number)

        except Exception as e:
            logger.error(f"Multi-round evaluation failed: {str(e)}")
            # Fallback evaluation
            return self._create_fallback_multi_round_evaluation(str(e), criteria, round_number, language)

    def _create_fallback_multi_round_evaluation(
        self,
        error: str,
        criteria: List[str],
        round_number: int,
        language: str = "zh-HK"
    ) -> MultiRoundEvaluationResult:
        """Create fallback multi-round evaluation when AI fails"""

        # Create default scores for criteria
        criteria_scores = {criterion: 2 for criterion in criteria}
        total_score = sum(criteria_scores.values())

        if language == "en":
            feedback = f"Evaluation system error, please retry. Error: {error}"
            detailed_feedback = {criterion: "System error" for criterion in criteria}
        else:
            feedback = f"評估系統出現錯誤，請重試。錯誤：{error}"
            detailed_feedback = {criterion: "系統錯誤" for criterion in criteria}

        return MultiRoundEvaluationResult(
            criteria_scores=criteria_scores,
            total_score=total_score,
            max_possible_score=len(criteria) * 3,  # Conservative estimate
            feedback=feedback,
            detailed_feedback=detailed_feedback,
            passed=False,
            round_number=round_number
        )