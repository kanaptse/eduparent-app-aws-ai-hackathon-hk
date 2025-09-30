"""Teen response generation agent"""

import json
from pydantic_ai import Agent
from ..config import ModelConfig
from ..models.evaluation import TeenResponse


class TeenResponderAgent:
    """Agent responsible for generating teen responses"""

    def __init__(self):
        self._agent = Agent(ModelConfig.get_teen_response_model())
        self._setup_system_prompt()

    def _setup_system_prompt(self):
        """Configure the teen response system prompt"""
        @self._agent.system_prompt
        def teen_prompt() -> str:
            return """You are a 14-year-old teenager responding to your parent in various scenarios.

Your response should be based on the parent's communication quality (score 0-10) and the specific scenario context provided.

RESPONSE GUIDELINES BY SCORE:

CANTONESE RESPONSES (language: zh-HK):
- Score 8-10: Cooperative, willing to listen and work together
- Score 6-7: Somewhat resistant but eventually willing to engage
- Score 4-5: Defensive, argumentative, pushing back
- Score 0-3: Very defensive, upset, feeling misunderstood

ENGLISH RESPONSES (language: en):
- Score 8-10: Cooperative, willing to listen and work together
- Score 6-7: Somewhat resistant but eventually willing to engage
- Score 4-5: Defensive, argumentative, pushing back
- Score 0-3: Very defensive, upset, feeling misunderstood

IMPORTANT:
- Base your response on the specific scenario context provided
- Stay in character as the child/teen in that scenario
- Don't reference cleaning, homework, or other unrelated activities
- Respond naturally to what the parent actually said

Return JSON with:
- response: str (your response in the specified language, appropriate to the scenario)
- emotion: str (cooperative/reluctant/defensive/upset)

Keep responses realistic for a 14-year-old in the given situation."""

    async def respond(self, score: int, context: str = "", language: str = "zh-HK") -> TeenResponse:
        """Generate teen response based on parent communication score"""

        if language == "en":
            context_part = f" Context: {context}" if context else ""
            prompt = f"""Parent's communication score is {score}/10. Please respond to the parent based on this score. Higher score means better parent communication, so your response should be more cooperative.{context_part}

Language: English
Return pure JSON format only, no other text."""
        else:
            context_part = f" 背景：{context}" if context else ""
            prompt = f"""父母嘅溝通得分係 {score}/10。請根據呢個分數回應父母嘅話。分數越高表示父母溝通越好，你嘅回應應該越配合。{context_part}

語言：廣東話
返回純JSON格式，唔好其他文字。"""

        try:
            result = await self._agent.run(prompt)

            # Clean up response
            output = self._clean_json_output(result.output)

            # Parse JSON
            teen_data = json.loads(output)

            return TeenResponse.from_dict(teen_data)

        except Exception:
            # Fallback response based on score and language
            return self._create_fallback_response(score, language)

    def _clean_json_output(self, output: str) -> str:
        """Clean up JSON output from AI response"""
        output = output.strip()
        if output.startswith('```json'):
            output = output[7:]
        if output.endswith('```'):
            output = output[:-3]
        return output.strip()

    def _create_fallback_response(self, score: int, language: str = "zh-HK") -> TeenResponse:
        """Create fallback response when AI fails"""
        if language == "en":
            if score >= 7:
                return TeenResponse(
                    response="Okay, I understand what you're saying",
                    emotion="cooperative"
                )
            else:
                return TeenResponse(
                    response="I don't want to talk about this right now",
                    emotion="defensive"
                )
        else:
            if score >= 7:
                return TeenResponse(
                    response="好啦，我明白你嘅意思",
                    emotion="cooperative"
                )
            else:
                return TeenResponse(
                    response="我而家唔想講呢啲",
                    emotion="defensive"
                )