from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime


class FeedItem(BaseModel):
    title: str
    text: str


class Card(BaseModel):
    id: str
    title: str
    content: str
    order: int


class ActionQuest(BaseModel):
    id: str
    title: str
    prompt: str
    input_placeholder: str


class CardStack(BaseModel):
    id: str
    title: str
    description: str
    cards: List[Card]
    summary: str
    action_quest: Optional[ActionQuest] = None
    estimated_read_time: int  # in minutes
    total_cards: int


class CardStackPreview(BaseModel):
    id: str
    title: str
    description: str
    total_cards: int
    estimated_read_time: int
    is_completed: bool = False


class UserProgress(BaseModel):
    stack_id: str
    user_id: str
    completed_cards: List[str]
    is_completed: bool = False
    last_card_index: int = 0


class ActionQuestResponse(BaseModel):
    quest_id: str
    user_id: str
    response_text: str
    timestamp: datetime


class EnhancedFeedItem(BaseModel):
    type: str  # "simple" or "card_stack"
    simple_item: Optional[FeedItem] = None
    stack_preview: Optional[CardStackPreview] = None


class EnhancedFeedResponse(BaseModel):
    items: List[EnhancedFeedItem]
    streak: int


class FeedResponse(BaseModel):
    items: List[FeedItem]
    streak: int


class CalculatorRequest(BaseModel):
    a: float
    b: float


class CalculatorResponse(BaseModel):
    result: float


class SurveyRequest(BaseModel):
    goal: str
    note: Optional[str] = ""


class SurveyResponse(BaseModel):
    goal: str
    note: str
    recommendation: str
    tiny_actions: List[str]