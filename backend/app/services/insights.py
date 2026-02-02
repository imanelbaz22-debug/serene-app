from app.db.models import CheckIn

def analyze_checkin(checkin: CheckIn):
    reasons = []
    tips = []

    # 1. Sleep Analysis
    if checkin.sleep_hours is not None:
        if checkin.sleep_hours < 5.0:
            reasons.append("Severe sleep deprivation")
            tips.append("Your brain needs recovery. Avoid caffeine after 2 PM. Tonight, try a 'digital sunset'—no screens 1 hour before bed—and keep your room cool (65°F/18°C) to maximize deep sleep.")
        elif checkin.sleep_hours < 7.0:
            reasons.append("Mild sleep debt")
            tips.append("You might feel irritable or groggy. Try the 4-7-8 breathing technique to fall asleep faster tonight: Inhale for 4s, hold for 7s, exhale for 8s.")
    
    # 2. Energy Analysis
    if checkin.energy is not None:
        if checkin.energy <= 3:
            reasons.append("Low physical energy")
            tips.append("Fatigue can trick you into low mood. Drink a large glass of water immediately (dehydration causes fatigue). A 10-minute walk outside will boost norepinephrine more effectively than sugar.")
        elif checkin.energy <= 5:
            tips.append("Your energy is middling. Change your environment—stand up, stretch, or move to a different room to reset your focus.")

    # 3. Mood Analysis & Keyword Scanning
    # We analyze text even if mood is okay, but prioritize it if mood is low.
    text = (checkin.text or "").lower()
    
    import re
    def contains_word(text, words):
        # Create a regex pattern to match any of the words as whole words
        pattern = r'\b(?:' + '|'.join(re.escape(word) for word in words) + r')\b'
        return bool(re.search(pattern, text))

    # Relationship Advice
    # Relationship Advice Logic Refinement
    # Split keywords into entities and conflict indicators to avoid false positives
    RELATIONSHIP_ENTITIES = ["partner", "wife", "husband", "boyfriend", "girlfriend", "spouse", "fiance"]
    CONFLICT_INDICATORS = ["fight", "argument", "conflict", "clash", "disagreement", "mad", "angry", "annoyed"]
    RELATIONSHIP_CRISES = ["breakup", "ex", "divorce", "separated", "broken up"]

    def has_relationship_stress():
        # 1. Immediate crisis keywords always trigger
        if contains_word(text, RELATIONSHIP_CRISES):
            return True
        
        # 2. Entity + (Conflict Word OR Low Mood)
        has_entity = contains_word(text, RELATIONSHIP_ENTITIES)
        if has_entity:
            has_conflict = contains_word(text, CONFLICT_INDICATORS)
            # If explicit conflict word is present, or mood is low (<=4) while mentioning partner
            if has_conflict or checkin.mood <= 4:
                return True
        
        return False

    if has_relationship_stress():
        reasons.append("Relationship conflict or strain")
        tips.append("RELATIONSHIP SOS: If emotions are high, take a strict 20-minute timeout to let stress hormones drop before talking again. When you resume, use 'I statements' ('I feel hurt when...') rather than accusations ('You always...'). This reduces defensiveness.")

    # Work/Career
    elif contains_word(text, ["work", "job", "project", "boss", "deadline", "career"]):
        reasons.append("Work-related pressure")
        tips.append("WORK FOCUS: Use the Eisenhower Matrix to sort tasks: do what is 'Urgent & Important' first. For everything else, schedule it or delegate it. Block time for 'deep work' (no notifications) to reduce the anxiety of multitasking.")

    # Academic/School
    elif contains_word(text, ["exam", "study", "school", "grade", "test", "homework"]):
        reasons.append("Academic stress")
        tips.append("STUDY HACK: Passive re-reading is inefficient. Use 'Active Recall'—test yourself on the material without looking. combine this with the Pomodoro technique (25min work, 5min break) to maintain peak cognitive performance.")

    # Loneliness/Social
    elif contains_word(text, ["lonely", "alone", "isolated", "sad", "miss"]):
        reasons.append("Social isolation")
        tips.append("CONNECTION: Social pain lights up the same brain regions as physical pain. Call (don't text) a friend or family member for just 5 minutes. Hearing a voice releases oxytocin which lowers cortisol.")

    # Financial (New)
    elif contains_word(text, ["money", "debt", "rent", "bill", "expensive", "cost"]):
        reasons.append("Financial anxiety")
        tips.append("FINANCE: Anxiety comes from uncertainty. Take 10 minutes today to just *list* your expenses. You don't need to solve it today, but accurately naming the problem reduces the brain's fear response.")

    # Health/Body
    elif contains_word(text, ["sick", "pain", "headache", "tired", "body"]):
        reasons.append("Physical discomfort")
        tips.append("Listen to your body. If you are in pain/sickness, your mood will naturally drop. Do not push through. Rest is productive when it heals you.")

    # Fallback if mood is low but no keywords matched
    if checkin.mood <= 4 and not reasons:
        reasons.append("General low mood")
        tips.append("Sometimes we feel down without a clear reason. That is valid. Try 'Behavioral Activation': do one small activity you usually enjoy, even if you don't feel like it. The action often creates the motivation, not the other way around.")

    # 4. Positive Reinforcement
    if checkin.mood >= 8:
        if not reasons: # Only add if we haven't found a specific stressor (sometimes people embrace stress!)
            reasons.append("Positive State")
            tips.append("You are thriving! Take a moment to savor *exactly* why you feel good (write it down). Savoring positive experiences builds neural pathways that make resilience easier later.")

    return {
        "reasons": reasons,
        "tips": tips
    }
