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
    
    # Relationship Advice
    if any(word in text for word in ["fight", "argument", "partner", "wife", "husband", "boyfriend", "girlfriend", "breakup", "ex"]):
        reasons.append("Relationship conflict or strain")
        tips.append("RELATIONSHIP SOS: If emotions are high, take a strict 20-minute timeout to let stress hormones drop before talking again. When you resume, use 'I statements' ('I feel hurt when...') rather than accusations ('You always...'). This reduces defensiveness.")

    # Work/Career
    elif any(word in text for word in ["work", "job", "project", "boss", "deadline", "career"]):
        reasons.append("Work-related pressure")
        tips.append("WORK FOCUS: Use the Eisenhower Matrix to sort tasks: do what is 'Urgent & Important' first. For everything else, schedule it or delegate it. Block time for 'deep work' (no notifications) to reduce the anxiety of multitasking.")

    # Academic/School
    elif any(word in text for word in ["exam", "study", "school", "grade", "test", "homework"]):
        reasons.append("Academic stress")
        tips.append("STUDY HACK: Passive re-reading is inefficient. Use 'Active Recall'—test yourself on the material without looking. combine this with the Pomodoro technique (25min work, 5min break) to maintain peak cognitive performance.")

    # Loneliness/Social
    elif any(word in text for word in ["lonely", "alone", "isolated", "sad", "miss"]):
        reasons.append("Social isolation")
        tips.append("CONNECTION: Social pain lights up the same brain regions as physical pain. Call (don't text) a friend or family member for just 5 minutes. Hearing a voice releases oxytocin which lowers cortisol.")

    # Financial (New)
    elif any(word in text for word in ["money", "debt", "rent", "bill", "expensive", "cost"]):
        reasons.append("Financial anxiety")
        tips.append("FINANCE: Anxiety comes from uncertainty. Take 10 minutes today to just *list* your expenses. You don't need to solve it today, but accurately naming the problem reduces the brain's fear response.")

    # Health/Body
    elif any(word in text for word in ["sick", "pain", "headache", "tired", "body"]):
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
