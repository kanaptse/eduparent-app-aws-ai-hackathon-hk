from fastapi import APIRouter
from app.models.schemas import FeedItem, FeedResponse, EnhancedFeedResponse
from app.services.feed_service import get_daily_feed, get_enhanced_daily_feed

router = APIRouter()

@router.get("/daily", response_model=FeedResponse)
async def get_daily_feed_items():
    """Get today's 3 simple feed items (legacy endpoint)"""
    return await get_daily_feed()

@router.get("/enhanced", response_model=EnhancedFeedResponse)
async def get_enhanced_daily_feed_items(language: str = "zh-HK"):
    """Get today's enhanced feed with mix of simple items and card stack previews"""
    return await get_enhanced_daily_feed(language)

@router.post("/mark-read/{item_id}")
async def mark_item_read(item_id: int):
    """Mark a simple feed item as read"""
    # This would typically update user progress in database
    return {"success": True, "item_id": item_id}

@router.post("/mark-stack-completed/{stack_id}")
async def mark_stack_completed(stack_id: str, user_id: str = "default_user"):
    """Mark a card stack as completed"""
    # This would typically update user progress in database
    return {"success": True, "stack_id": stack_id, "user_id": user_id}

@router.get("/streak/{user_id}")
async def get_user_streak(user_id: str):
    """Get user's current streak"""
    # This would typically fetch from database
    return {"streak": 0}