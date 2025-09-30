from typing import Dict, List, Optional
from app.models.schemas import Card, CardStack, ActionQuest, CardStackPreview, UserProgress


# Emotion Labeling Card Stack Content (Chinese)
EMOTION_LABELING_CARDS_ZH = [
    Card(
        id="amygdala_basics",
        title="杏仁核（Amygdala）是什麼？",
        content="""杏仁核是大腦中負責 **情緒處理、威脅偵測、壓力反應** 的核心區域。

當孩子感到生氣、焦慮、害怕時，杏仁核會被強烈激活 → 觸發 **戰或逃反應**（fight-or-flight）。

一旦杏仁核處於高亢狀態，孩子的情緒會被「劫持」，**難以冷靜下來思考**。

🧠 **關鍵理解**：情緒爆發時，孩子的理性思考能力會暫時下降，這不是故意的，而是大腦的自然反應。""",
        order=1
    ),
    Card(
        id="parental_reactions",
        title="父母不當反應如何加劇杏仁核反應？",
        content="""以下反應會讓孩子的杏仁核持續過度激活：

❌ **否定情緒**：「不要哭了，這有什麼好傷心的」
❌ **轉移問題**：「快點去做功課，不要想這些」  
❌ **過度批評**：「你怎麼這麼小事也發脾氣！」

這些反應會讓孩子覺得情緒「不被允許、不被理解」 → 杏仁核持續過度激活，情緒壓力加深。

💡 **重點**：當我們否定孩子的情緒時，實際上是在延長他們的痛苦，而不是在幫助他們。""",
        order=2
    ),
    Card(
        id="neuroscience_effects",
        title="情緒命名的神經科學效果",
        content="""🔬 **科學發現**：加州大學洛杉磯分校 (UCLA) 的 fMRI 研究發現：

當人把情緒用語言標籤化（例如「我很焦慮」），**杏仁核的活化會顯著下降**。

同時，大腦前額葉皮層（prefrontal cortex，掌管理性思考、專注、抑制衝動）會被更多啟動。

⚡ **神奇轉換**：情緒命名 = 從杏仁核接管情緒，轉交給理智腦處理

這就是為什麼簡單的一句「你是不是覺得很沮喪？」就能讓孩子快速冷靜下來。""",
        order=3
    ),
    Card(
        id="psychological_impact",
        title="對心理和學習的影響",
        content="""長期影響包括：

📚 **學習表現**  
當杏仁核過度激活，前額葉功能下降 → 注意力和工作記憶受影響，孩子無法好好學習。

💗 **心理健康**  
長期忽略或否定情緒 → 造成孩子情緒調節困難，增加焦慮、抑鬱風險。

👥 **人際關係**  
學不會辨識和調節情緒的孩子，容易在人際互動中爆發衝突。

✨ **正向循環**：情緒命名 → 情緒穩定 → 學習能力提升 → 自信增加""",
        order=4
    ),
    Card(
        id="practical_application",
        title="父母如何應用「情緒命名」？",
        content="""四步驟實踐法：

1️⃣ **觀察** → 注意孩子的表情、語氣、動作

2️⃣ **命名** → 嘗試用語言標籤情緒：「你是不是覺得很失望？」

3️⃣ **確認** → 讓孩子修正或補充：「不是失望，是有點生氣。」

4️⃣ **接納** → 表達理解：「嗯，我懂，這真的會讓人很沮喪。」

🎯 **神奇效果**：
- 幫孩子「大腦翻譯」情緒，降低杏仁核激活
- 孩子覺得「被理解」，安全感提升  
- 情緒穩定後，才有空間討論解決問題""",
        order=5
    ),
    Card(
        id="daily_practice",
        title="今天開始的小練習",
        content="""🌟 **立即可行的方法**：

**場景示例**：
- 孩子考試考砸了，在房間生悶氣
- ❌ 舊方式：「考砸就考砸，下次努力就好了」
- ✅ 新方式：「你是不是覺得很挫折？這種感覺我懂...」

**今日挑戰**：
找一個時機，當孩子有情緒時，先嘗試幫他命名：
「你是不是覺得有點緊張？」「聽起來你很沮喪？」

🎁 **額外收穫**：當孩子感受到被理解，他們更願意跟你分享內心想法，親子關係會更親密。""",
        order=6
    )
]


# Emotion Labeling Card Stack Content (English)
EMOTION_LABELING_CARDS_EN = [
    Card(
        id="amygdala_basics",
        title="What is the Amygdala?",
        content="""The amygdala is the core brain region responsible for **emotional processing, threat detection, and stress response**.

When children feel angry, anxious, or afraid, the amygdala becomes highly activated → triggering the **fight-or-flight response**.

Once the amygdala is in a heightened state, children's emotions become "hijacked," making it **difficult to calm down and think rationally**.

🧠 **Key Understanding**: During emotional outbursts, children's rational thinking ability temporarily decreases. This isn't intentional—it's the brain's natural response.""",
        order=1
    ),
    Card(
        id="parental_reactions",
        title="How Poor Parental Responses Amplify Amygdala Activation",
        content="""The following responses keep children's amygdalae in overdrive:

❌ **Dismissing emotions**: "Stop crying, there's nothing to be sad about"
❌ **Deflecting the issue**: "Just go do your homework, don't think about this"
❌ **Excessive criticism**: "Why do you get upset over such small things!"

These responses make children feel their emotions are "not allowed, not understood" → keeping the amygdala overactive and deepening emotional distress.

💡 **Key Point**: When we dismiss children's emotions, we're actually prolonging their suffering rather than helping them.""",
        order=2
    ),
    Card(
        id="neuroscience_effects",
        title="The Neuroscience of Emotion Labeling",
        content="""🔬 **Scientific Discovery**: UCLA fMRI research found:

When people verbally label emotions (e.g., "I feel anxious"), **amygdala activation significantly decreases**.

Simultaneously, the prefrontal cortex (responsible for rational thinking, focus, and impulse control) becomes more activated.

⚡ **The Magic Switch**: Emotion labeling = transferring control from the emotional amygdala to the rational brain

This is why a simple phrase like "Are you feeling frustrated?" can quickly help children calm down.""",
        order=3
    ),
    Card(
        id="psychological_impact",
        title="Impact on Psychology and Learning",
        content="""Long-term effects include:

📚 **Academic Performance**
When the amygdala is overactive, prefrontal function decreases → attention and working memory are impaired, preventing effective learning.

💗 **Mental Health**
Chronic emotion dismissal → leads to emotional regulation difficulties and increased risk of anxiety and depression.

👥 **Relationships**
Children who don't learn to identify and regulate emotions tend to have explosive conflicts in social interactions.

✨ **Positive Cycle**: Emotion labeling → emotional stability → improved learning ability → increased confidence""",
        order=4
    ),
    Card(
        id="practical_application",
        title="How Parents Can Apply 'Emotion Labeling'",
        content="""Four-step practice method:

1️⃣ **Observe** → Notice your child's facial expressions, tone, and body language

2️⃣ **Label** → Try to verbally identify the emotion: "Are you feeling disappointed?"

3️⃣ **Confirm** → Let your child correct or add: "Not disappointed, but a bit angry."

4️⃣ **Accept** → Express understanding: "I get it, that would be really frustrating."

🎯 **Amazing Effects**:
- Helps children "translate" emotions in their brain, reducing amygdala activation
- Children feel "understood," increasing their sense of safety
- Once emotions stabilize, there's space to discuss problem-solving""",
        order=5
    ),
    Card(
        id="daily_practice",
        title="Small Practice to Start Today",
        content="""🌟 **Immediately Actionable Method**:

**Scenario Example**:
- Child failed a test and is sulking in their room
- ❌ Old way: "It's just one test, work harder next time"
- ✅ New way: "Are you feeling frustrated? I understand that feeling..."

**Today's Challenge**:
Find an opportunity when your child is emotional and try to help them label it:
"Are you feeling a bit nervous?" "It sounds like you're really disappointed?"

🎁 **Bonus Benefit**: When children feel understood, they're more willing to share their inner thoughts, making parent-child relationships more intimate.""",
        order=6
    )
]


EMOTION_LABELING_ACTION_QUEST_ZH = ActionQuest(
    id="emotion_naming_practice",
    title="今天的行動挑戰",
    prompt="嘗試在孩子有情緒時，先幫他命名情緒，而不是急著解決問題。觀察孩子的反應。",
    input_placeholder="記錄：什麼情況下嘗試了情緒命名？孩子的反應如何？你觀察到什麼變化？"
)

EMOTION_LABELING_ACTION_QUEST_EN = ActionQuest(
    id="emotion_naming_practice",
    title="Today's Action Challenge",
    prompt="When your child shows emotions, try to help them label their feelings instead of rushing to solve the problem. Observe their response.",
    input_placeholder="Record: In what situation did you try emotion labeling? How did your child respond? What changes did you notice?"
)


def create_emotion_labeling_stack(language: str = "zh-HK") -> CardStack:
    """Create emotion labeling stack in the specified language"""
    if language == "en":
        return CardStack(
            id="emotion_labeling",
            title="The Science of Emotion Labeling",
            description="Understand your child's emotions through neuroscience and learn simple, effective emotion labeling techniques",
            cards=EMOTION_LABELING_CARDS_EN,
            summary="""🎯 **Key Takeaways**:

• **Amygdala Activation** → During emotional outbursts, children's rational thinking decreases
• **Emotion Labeling** → Effectively reduces amygdala activation and engages the rational brain
• **Four Steps**: Observe → Label → Confirm → Accept
• **Amazing Effect**: Children who feel understood calm down easier and learn better

Start practicing today: when your child shows emotion, try saying "Are you feeling...?" """,
            action_quest=None,  # Removed action quest - keep as separate feature
            estimated_read_time=8,
            total_cards=6
        )
    else:  # Default to Chinese
        return CardStack(
            id="emotion_labeling",
            title="情緒命名的科學基礎",
            description="用神經科學理解孩子情緒，學會簡單有效的情緒命名技巧",
            cards=EMOTION_LABELING_CARDS_ZH,
            summary="""🎯 **重點回顧**：

• **杏仁核激活** → 孩子情緒爆發時，理性思考能力下降
• **情緒命名** → 能有效降低杏仁核活化，啟動理智腦
• **四步驟**：觀察 → 命名 → 確認 → 接納
• **神奇效果**：被理解的孩子更容易冷靜，學習效果更好

今天就開始練習，當孩子有情緒時，試著說：「你是不是覺得...？」""",
            action_quest=None,  # Removed action quest - keep as separate feature
            estimated_read_time=8,
            total_cards=6
        )


# Active Listening Card Stack Content
ACTIVE_LISTENING_CARDS = [
    Card(
        id="listening_barriers",
        title="Why Traditional Listening Fails with Children",
        content="""Common listening mistakes that shut down communication:

❌ **Immediate Problem-Solving**: "Just do this..." - Skips emotional validation
❌ **Minimizing Feelings**: "It's not that big a deal" - Dismisses their experience  
❌ **Divided Attention**: Listening while on phone/computer - Shows disrespect
❌ **Interrogation Mode**: Rapid-fire questions - Creates pressure, not connection

🧠 **The Science**: When children feel unheard, their stress hormones (cortisol) increase, making them less receptive to guidance or solutions.

💡 **Key Insight**: Children need to feel **felt** before they can hear your wisdom.""",
        order=1
    ),
    Card(
        id="full_presence",
        title="The Power of Full Presence",
        content="""Active listening starts with **full presence** - giving your complete attention.

🎯 **Physical Presence**:
- Put devices away completely
- Turn your body toward your child
- Make appropriate eye contact (not staring)
- Get on their physical level if they're young

⚡ **Mental Presence**:
- Stop thinking about responses while they talk
- Notice when your mind wanders to other topics
- Release your agenda to "fix" or "teach"

🔬 **Research**: Children can detect partial attention within seconds. Full presence activates their parasympathetic nervous system, creating safety for deeper sharing.""",
        order=2
    ),
    Card(
        id="reflective_listening",
        title="Reflective Listening: The Mirror Technique",
        content="""Reflective listening mirrors back what your child is communicating - both content and emotion.

**The Formula**: "You're saying [content] and you feel [emotion]."

**Examples**:
- Child: "I hate math! It's stupid and I'm never going to use it!"
- ❌ Poor: "Math is important for your future."
- ✅ Good: "You're saying math feels pointless and you're frustrated with it."

**Benefits**:
- Shows you're truly listening
- Helps child feel understood
- Clarifies their actual concern
- Calms their nervous system

🎯 **Practice**: Don't add advice. Just reflect. Watch how this changes the conversation dynamic.""",
        order=3
    ),
    Card(
        id="emotion_behind_words",
        title="Listening for Emotions Behind Words",
        content="""Children often express emotions indirectly. Learn to hear the feeling under the words.

**Translation Examples**:
- "This is boring" → Often means: "I'm frustrated" or "I don't understand"
- "You're mean" → Often means: "I feel powerless" or "I'm hurt"
- "I don't care" → Often means: "I care too much and I'm protecting myself"

**Listening Technique**:
1. Listen to their words
2. Notice their tone and body language  
3. Ask yourself: "What emotion might be driving this?"
4. Reflect the emotion: "It sounds like you're feeling..."

🧠 **Developmental Note**: Younger children (under 10) often can't articulate emotions directly. Your emotional translation helps develop their emotional vocabulary.""",
        order=4
    ),
    Card(
        id="strategic_silence",
        title="The Strategic Power of Silence",
        content="""Silence is one of the most powerful listening tools - but it feels uncomfortable for parents.

**Why Silence Works**:
- Gives children time to process their thoughts
- Shows you're not rushing to judgment
- Allows deeper emotions to surface
- Prevents you from interrupting their flow

**How to Use Silence**:
- After they finish speaking, wait 3-5 seconds
- Use gentle nodding or "mm-hmm" to show engagement
- Resist the urge to fill the space with questions
- Let them guide what they want to share next

⚠️ **Common Parent Fear**: "If I don't respond, they'll think I don't care."
✅ **Reality**: Silence often communicates deeper care than immediate responses.""",
        order=5
    ),
    Card(
        id="listening_practice",
        title="Daily Active Listening Practice",
        content="""**The 10-Minute Connection Ritual**:
Choose a consistent time daily for device-free, agenda-free listening.

**Structure**:
1. **Set the stage**: "I have 10 minutes and I'm all yours. What's on your mind?"
2. **Listen without agenda**: No teaching, fixing, or problem-solving
3. **Use reflective responses**: "You're saying..." "It sounds like..."
4. **End with appreciation**: "Thank you for sharing that with me."

**Week 1 Challenge**: Practice pure listening - no advice giving
**Week 2 Challenge**: Add emotion reflection  
**Week 3 Challenge**: Notice their body language changes when truly heard

🎁 **Parent Feedback**: "My 12-year-old said, 'Mom, you listen different now. I like talking to you more.'" """,
        order=6
    )
]

ACTIVE_LISTENING_ACTION_QUEST = ActionQuest(
    id="active_listening_practice",
    title="今天的聆聽挑戰",
    prompt="實踐全神貫注的聆聽：放下所有裝置，給孩子10分鐘完全的注意力。不要急著給建議，只要反映你聽到的內容和情緒。",
    input_placeholder="記錄：什麼情況下練習了專注聆聽？孩子分享了什麼？你注意到他們的反應有什麼變化？"
)

ACTIVE_LISTENING_STACK = CardStack(
    id="active_listening",
    title="Active Listening: The Foundation of Connection",
    description="Master the art of truly hearing your child through evidence-based listening techniques that build trust and deepen relationships",
    cards=ACTIVE_LISTENING_CARDS,
    summary="""🎯 **Key Takeaways**:

• **Full Presence** → Put devices away, make eye contact, give complete attention
• **Reflective Listening** → Mirror back content and emotions: "You're saying... and you feel..."
• **Emotion Translation** → Listen for feelings behind words: "boring" often means "frustrated"
• **Strategic Silence** → 3-5 seconds of silence allows deeper sharing
• **Daily Practice** → 10-minute device-free connection time builds listening habits

Start today: Ask your child "What's on your mind?" and practice pure listening for 10 minutes.""",
    action_quest=None,  # Removed action quest for English version
    estimated_read_time=10,
    total_cards=6
)

# Card Stack Registry (for backwards compatibility, using Chinese as default)
CARD_STACKS: Dict[str, CardStack] = {
    "emotion_labeling": create_emotion_labeling_stack("zh-HK"),
    "active_listening": ACTIVE_LISTENING_STACK
}


async def get_card_stack(stack_id: str, language: str = "zh-HK") -> Optional[CardStack]:
    """Get a specific card stack by ID with language support"""
    if stack_id == "emotion_labeling":
        return create_emotion_labeling_stack(language)
    return CARD_STACKS.get(stack_id)


async def get_all_card_stack_previews() -> List[CardStackPreview]:
    """Get previews of all available card stacks"""
    previews = []
    for stack in CARD_STACKS.values():
        preview = CardStackPreview(
            id=stack.id,
            title=stack.title,
            description=stack.description,
            total_cards=stack.total_cards,
            estimated_read_time=stack.estimated_read_time,
            is_completed=False  # TODO: Check user progress
        )
        previews.append(preview)
    return previews


async def get_card_stack_preview(stack_id: str, language: str = "zh-HK") -> Optional[CardStackPreview]:
    """Get preview of a specific card stack with language support"""
    stack = await get_card_stack(stack_id, language)
    if not stack:
        return None

    return CardStackPreview(
        id=stack.id,
        title=stack.title,
        description=stack.description,
        total_cards=stack.total_cards,
        estimated_read_time=stack.estimated_read_time,
        is_completed=False  # TODO: Check user progress
    )


# TODO: Implement user progress tracking with database
async def save_user_progress(progress: UserProgress) -> bool:
    """Save user progress (placeholder for database implementation)"""
    # This would save to database in real implementation
    return True


async def get_user_progress(stack_id: str, user_id: str) -> Optional[UserProgress]:
    """Get user progress for a card stack (placeholder for database implementation)"""
    # This would fetch from database in real implementation  
    return None