from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    CardStack, CardStackPreview, UserProgress, ActionQuestResponse
)
from app.services.card_stack_service import (
    get_card_stack, get_all_card_stack_previews, 
    get_card_stack_preview, save_user_progress, get_user_progress
)
from datetime import datetime
from typing import List

router = APIRouter()


@router.get("/previews", response_model=List[CardStackPreview])
async def get_card_stack_previews():
    """Get previews of all available card stacks"""
    return await get_all_card_stack_previews()


@router.get("/{stack_id}/preview", response_model=CardStackPreview)
async def get_stack_preview(stack_id: str):
    """Get preview of a specific card stack"""
    preview = await get_card_stack_preview(stack_id)
    if not preview:
        raise HTTPException(status_code=404, detail="Card stack not found")
    return preview


@router.get("/{stack_id}", response_model=CardStack)
async def get_stack(stack_id: str, language: str = "zh-HK"):
    """Get complete card stack content"""
    stack = await get_card_stack(stack_id, language=language)
    if not stack:
        raise HTTPException(status_code=404, detail="Card stack not found")
    return stack


@router.get("/{stack_id}/card/{card_index}")
async def get_card_by_index(stack_id: str, card_index: int):
    """Get a specific card from a stack by index"""
    stack = await get_card_stack(stack_id)
    if not stack:
        raise HTTPException(status_code=404, detail="Card stack not found")
    
    if card_index < 0 or card_index >= len(stack.cards):
        raise HTTPException(status_code=404, detail="Card not found")
    
    card = stack.cards[card_index]
    return {
        "card": card,
        "current_index": card_index,
        "total_cards": len(stack.cards),
        "is_last_card": card_index == len(stack.cards) - 1
    }


@router.post("/{stack_id}/progress")
async def update_progress(stack_id: str, user_id: str, completed_card_id: str):
    """Update user progress for a card stack"""
    # Get current progress or create new
    progress = await get_user_progress(stack_id, user_id)
    if not progress:
        progress = UserProgress(
            stack_id=stack_id,
            user_id=user_id,
            completed_cards=[],
            is_completed=False,
            last_card_index=0
        )
    
    # Add completed card if not already added
    if completed_card_id not in progress.completed_cards:
        progress.completed_cards.append(completed_card_id)
    
    # Get stack to check completion
    stack = await get_card_stack(stack_id)
    if stack:
        progress.is_completed = len(progress.completed_cards) >= len(stack.cards)
        
        # Update last card index
        for i, card in enumerate(stack.cards):
            if card.id == completed_card_id:
                progress.last_card_index = i
                break
    
    # Save progress
    await save_user_progress(progress)
    
    return {
        "success": True,
        "progress": progress
    }


@router.get("/{stack_id}/progress/{user_id}", response_model=UserProgress)
async def get_progress(stack_id: str, user_id: str):
    """Get user progress for a card stack"""
    progress = await get_user_progress(stack_id, user_id)
    if not progress:
        # Return default progress if none exists
        return UserProgress(
            stack_id=stack_id,
            user_id=user_id,
            completed_cards=[],
            is_completed=False,
            last_card_index=0
        )
    return progress


@router.post("/{stack_id}/action-quest/response")
async def submit_action_quest_response(
    stack_id: str, 
    quest_id: str, 
    user_id: str, 
    response_text: str
):
    """Submit response to action quest"""
    response = ActionQuestResponse(
        quest_id=quest_id,
        user_id=user_id,
        response_text=response_text,
        timestamp=datetime.now()
    )
    
    # TODO: Save to database
    # await save_action_quest_response(response)
    
    return {
        "success": True,
        "message": "Response saved successfully",
        "response": response
    }


@router.get("/{stack_id}/action-quest/responses/{user_id}")
async def get_user_action_quest_responses(stack_id: str, user_id: str):
    """Get user's action quest responses for a stack"""
    # TODO: Implement database query
    return {
        "stack_id": stack_id,
        "user_id": user_id,
        "responses": []  # Placeholder
    }