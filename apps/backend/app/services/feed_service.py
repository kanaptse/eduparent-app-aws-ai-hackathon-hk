from datetime import datetime
from typing import List
from app.models.schemas import (
    FeedItem, FeedResponse, EnhancedFeedItem, EnhancedFeedResponse, 
    CardStackPreview
)
from app.services.card_stack_service import get_all_card_stack_previews


SIMPLE_FEED_ITEMS = [
    FeedItem(title="Practice emotion labeling", text="When your child seems upset, try: 'You look frustrated. Is that what you're feeling?' This activates their prefrontal cortex and calms the amygdala."),
    FeedItem(title="Use the 6-second rule", text="When anger triggers, wait 6 seconds before responding. Neurochemical floods peak and start to recede in this time, preventing reactive communication."),
    FeedItem(title="Mirror your child's emotions", text="Reflect their emotional state: 'I can see you're really disappointed about this.' This validates their experience and builds emotional intelligence."),
    FeedItem(title="Ask about their internal experience", text="Try: 'What's going on inside for you right now?' This helps children develop emotional awareness and self-reflection skills."),
    FeedItem(title="Validate before you educate", text="Acknowledge feelings first, then problem-solve. 'That sounds really hard' comes before 'Here's what we can do about it.'"),
    FeedItem(title="Use developmental empathy", text="Remember: A 7-year-old's brain processes differently than a 14-year-old's. Adjust your communication expectations to match their cognitive development."),
    FeedItem(title="Practice active listening", text="Put devices away, make eye contact, and repeat back what you heard: 'So you're saying...' This builds trust and connection."),
    FeedItem(title="Notice your own triggers", text="When you feel defensive or angry, take a breath. Your emotional regulation teaches your child how to manage their own emotions."),
    FeedItem(title="Ask open-ended questions", text="Replace 'How was school?' with 'What was the most interesting part of your day?' Open questions invite deeper sharing."),
    FeedItem(title="Use collaborative language", text="Try 'How can we solve this together?' instead of 'Here's what you need to do.' This builds partnership rather than power struggles."),
    FeedItem(title="Acknowledge their perspective", text="Even when you disagree, validate their viewpoint: 'I can understand why you'd see it that way.' This doesn't mean agreement, just understanding."),
    FeedItem(title="Practice repair conversations", text="When communication goes wrong, circle back: 'I didn't handle that well. Can we try again?' This models accountability and resilience."),
]


async def get_daily_feed() -> FeedResponse:
    """Get today's 3 simple feed items (legacy endpoint)"""
    seed = datetime.now().day
    today_items = [
        SIMPLE_FEED_ITEMS[(seed) % len(SIMPLE_FEED_ITEMS)],
        SIMPLE_FEED_ITEMS[(seed + 1) % len(SIMPLE_FEED_ITEMS)],
        SIMPLE_FEED_ITEMS[(seed + 2) % len(SIMPLE_FEED_ITEMS)],
    ]
    
    # In a real app, this would fetch user's actual streak from database
    streak = 0
    
    return FeedResponse(items=today_items, streak=streak)


async def get_enhanced_daily_feed(language: str = "zh-HK") -> EnhancedFeedResponse:
    """Get today's enhanced feed with language-specific card stack"""

    # Both languages show the same content (emotion labeling) with appropriate translations
    stack_id = "emotion_labeling"

    # Get the specific card stack preview with language parameter
    from app.services.card_stack_service import get_card_stack_preview
    stack_preview = await get_card_stack_preview(stack_id, language=language)

    enhanced_items: List[EnhancedFeedItem] = []

    # Add the language-appropriate card stack
    if stack_preview:
        enhanced_items.append(EnhancedFeedItem(
            type="card_stack",
            stack_preview=stack_preview
        ))

    # In a real app, this would fetch user's actual streak from database
    streak = 0

    return EnhancedFeedResponse(items=enhanced_items, streak=streak)