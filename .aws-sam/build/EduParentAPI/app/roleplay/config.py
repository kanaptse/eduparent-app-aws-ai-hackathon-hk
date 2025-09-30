"""Configuration management for the roleplay game"""

import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelConfig:
    """AI Model configuration from environment variables"""

    # Model selection
    EVALUATION_MODEL = os.getenv('EVALUATION_MODEL', 'openai:gpt-4o-mini')
    TEEN_RESPONSE_MODEL = os.getenv('TEEN_RESPONSE_MODEL', 'openai:gpt-4o-mini')

    # Model parameters
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

    @classmethod
    def get_evaluation_model(cls) -> str:
        """Get the model for evaluation tasks"""
        logger.info(f"Using evaluation model: {cls.EVALUATION_MODEL}")
        return cls.EVALUATION_MODEL

    @classmethod
    def get_teen_response_model(cls) -> str:
        """Get the model for teen response generation"""
        logger.info(f"Using teen response model: {cls.TEEN_RESPONSE_MODEL}")
        return cls.TEEN_RESPONSE_MODEL


class GameConfig:
    """Game-specific configuration"""

    MAX_ATTEMPTS = int(os.getenv('MAX_ATTEMPTS', '3'))
    PASS_THRESHOLD = int(os.getenv('PASS_THRESHOLD', '7'))

    # Scenario settings - adjust path for main backend
    SCENARIOS_DIR = os.getenv('SCENARIOS_DIR', 'app/roleplay/scenarios/data')