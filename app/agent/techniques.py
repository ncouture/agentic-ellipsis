"""Step-by-step interviewing and elicitation techniques catalog.

Provides structured lessons for teaching interviewing techniques step-by-step,
grounded in the Behavioral Table of Elements (BTOE), Deception Rating Scale (DRS),
Authority Pillars, and Ellipsis Dialogue methodologies.
"""

from __future__ import annotations

from typing import Any


TECHNIQUES: dict[str, dict[str, Any]] = {
    "funnel_method": {
        "id": "funnel_method",
        "title": "The Funnel Questioning Technique",
        "category": "questioning_strategy",
        "aliases": ["funnel", "funneling", "the funnel", "funnel technique", "funnel questioning"],
        "overview": (
            "A structured interrogation and interview technique that moves systematically "
            "from broad open-ended questions down to specific clarifiers, and finally to direct "
            "inconsistency tests. It locks down a subject's story without alerting them to what "
            "you are investigating."
        ),
        "steps": [
            {
                "step": 1,
                "title": "Broad Open-Ended Inquiry",
                "objective": "Establish the narrative arc and allow the subject to speak freely without interruption.",
                "guidance": (
                    "Ask wide, non-leading questions that invite an extended story. "
                    "Resist the urge to interrupt or point out inconsistencies. Note what they "
                    "emphasize, what time gaps they gloss over, and their baseline fluency."
                ),
                "example_dialogue": (
                    "Walk me through your entire shift yesterday, starting from when you arrived at the office "
                    "until you packed up to leave for the day."
                ),
                "behavioral_cues_to_watch": (
                    "Watch for skipped time intervals, sudden pacing changes, and spontaneous qualifiers "
                    "('honestly', 'as far as I remember'). Genuine memory usually includes minor incidental details."
                ),
                "pitfalls": (
                    "Asking leading or yes/no questions too early, which limits information flow and reveals "
                    "what you already know."
                ),
            },
            {
                "step": 2,
                "title": "Specific Clarification and Expansion",
                "objective": "Zoom in on critical moments or omissions identified during Step 1 without signaling suspicion.",
                "guidance": (
                    "Pick one specific time block or interaction mentioned in Step 1. Ask for detailed "
                    "clarification using neutral, curious framing rather than an accusatory tone."
                ),
                "example_dialogue": (
                    "You mentioned stepping into the hallway around 3:15 PM to grab a coffee. Tell me a bit more "
                    "about who you crossed paths with while you were walking over."
                ),
                "behavioral_cues_to_watch": (
                    "Observe response latency (taking significantly longer to answer than in Step 1), eye darting, "
                    "or sudden clearing of the throat before speaking."
                ),
                "pitfalls": (
                    "Showing skepticism or disbelief, which raises the subject's defenses before their story is locked down."
                ),
            },
            {
                "step": 3,
                "title": "Direct Challenge and Inconsistency Testing",
                "objective": "Introduce objective anomalies or contradictory evidence directly to test the subject's explanation.",
                "guidance": (
                    "Present the discrepancy neutrally as a puzzle you need help resolving together, rather than "
                    "as a triumphant 'gotcha'. Give them space to explain or amend their statement."
                ),
                "example_dialogue": (
                    "Help me understand this: the access card logs show your badge tapped the server room door at 3:18 PM, "
                    "but you recalled being in the breakroom across the floor until 3:30. How does that fit together?"
                ),
                "behavioral_cues_to_watch": (
                    "Look for tell clusters: pacifying behaviors (neck touching, collar tugging), linguistic distancing "
                    "(dropping first-person pronouns), or sudden posture shifts."
                ),
                "pitfalls": (
                    "Becoming aggressive or argumentative, which causes the subject to shut down or become combative."
                ),
            },
            {
                "step": 4,
                "title": "Resolution and Statement Confirmation",
                "objective": "Secure a definitive final statement or admission and summarize commitments.",
                "guidance": (
                    "Summarize their final explanation using their own words. Ask if there is anything they need to "
                    "correct or add, ensuring no convenient ambiguities remain."
                ),
                "example_dialogue": (
                    "Just to make sure we're completely on the same page: you're stating that you did tap the door at 3:18 "
                    "to check if it was locked, but never propped it open. Is there anything else about that moment we haven't covered?"
                ),
                "behavioral_cues_to_watch": (
                    "Look for signs of relief (deep exhalation, dropping shoulders) if they've come clean, or sustained tension "
                    "and micro-smirks if they believe their deception succeeded."
                ),
                "pitfalls": (
                    "Leaving vague phrasing in the final statement that could allow the subject to backtrack later."
                ),
            },
        ],
    },
    "baseline_and_norming": {
        "id": "baseline_and_norming",
        "title": "Behavioral Baseline Calibration and Norming",
        "category": "calibration",
        "aliases": ["baseline", "norming", "calibration", "behavioral baseline", "baseline calibration"],
        "overview": (
            "Calibrating a subject's normal, truthful behavioral patterns (eye movement, voice pitch, response latency, "
            "breathing tempo, and gestures) during low-stakes interaction before introducing critical questions."
        ),
        "steps": [
            {
                "step": 1,
                "title": "Neutral Small Talk Calibration",
                "objective": "Observe truthful baseline indicators during zero-stakes, comfortable interaction.",
                "guidance": (
                    "Engage in brief, pleasant conversation about verifiable, harmless facts (commute, weather, basic role). "
                    "Focus entirely on cataloging their natural eye blink rate, voice volume, hand positions, and posture."
                ),
                "example_dialogue": (
                    "Thanks for coming in this morning. Did you have any trouble finding a parking spot outside? "
                    "How has your project been going this week?"
                ),
                "behavioral_cues_to_watch": (
                    "Catalog baseline indicators: resting blink rate (usually 15-20/min), natural smiling, relaxed shoulder "
                    "height, and resting speech rate."
                ),
                "pitfalls": (
                    "Rushing immediately into interrogation mode without establishing at least 60-90 seconds of true baseline."
                ),
            },
            {
                "step": 2,
                "title": "Cognitive Memory Calibration",
                "objective": "Observe normal cognitive processing when the subject accesses truthful memories.",
                "guidance": (
                    "Ask a question requiring actual thought and memory recall, but with zero threat or emotional pressure. "
                    "Watch their gaze direction and facial muscle activation when retrieving honest information."
                ),
                "example_dialogue": (
                    "Can you remind me how your team usually coordinates the weekend on-call schedule? Who handles the rotation?"
                ),
                "behavioral_cues_to_watch": (
                    "Notice normal recall gestures: looking up or away during memory retrieval, natural pauses followed "
                    "by smooth speech once memory is recalled."
                ),
                "pitfalls": (
                    "Mistaking normal cognitive thinking pauses for deception or hesitation."
                ),
            },
            {
                "step": 3,
                "title": "The Sensitive Topic Transition",
                "objective": "Introduce the investigative topic calmly and monitor immediate autonomic reactions.",
                "guidance": (
                    "Transition smoothly into the subject of interest. Do not accuse; state the topic plainly and watch "
                    "for instantaneous deviations from the baseline established in Steps 1 and 2."
                ),
                "example_dialogue": (
                    "The specific reason I asked you to stop by is that our routine security sweep showed the server door "
                    "was unlatched overnight on Tuesday, and we need to understand what happened."
                ),
                "behavioral_cues_to_watch": (
                    "Immediate autonomic spikes: hard swallow (thyroid cartilage movement), throat clearing, sudden blink "
                    "bursts, or freezing in place (stillness tell)."
                ),
                "pitfalls": (
                    "Using accusatory or harsh inflection that triggers stress in innocent subjects as well as guilty ones."
                ),
            },
            {
                "step": 4,
                "title": "Deviation and Delta Isolation",
                "objective": "Compare behavior under investigative questions directly against the recorded baseline.",
                "guidance": (
                    "Measure any behavioral shift: Did speech slow down or speed up? Did eye contact dramatically increase "
                    "(compensatory staring) or disappear? Mark specific questions that triggered baseline shifts."
                ),
                "example_dialogue": (
                    "When you walked through that door around 9:30 PM, did you latch it securely behind you?"
                ),
                "behavioral_cues_to_watch": (
                    "Look for discordance between verbal and non-verbal channels—e.g. nodding 'yes' while saying 'no', "
                    "or pacifying gestures targeting the suprasternal notch or neck."
                ),
                "pitfalls": (
                    "Treating a single deviation as conclusive proof of a lie rather than as an indicator pointing toward "
                    "topics needing deeper probing."
                ),
            },
        ],
    },
    "cognitive_load": {
        "id": "cognitive_load",
        "title": "Cognitive Load Induction and Timeline Testing",
        "category": "cognitive_load",
        "aliases": ["cognitive load", "timeline testing", "reverse chronology", "cognitive interviewing"],
        "overview": (
            "Lying requires substantially more mental effort than telling the truth. By systematically increasing "
            "cognitive load (such as requiring reverse-chronological recall or probing unanticipated sensory details), "
            "a deceptive subject's cognitive capacity is overwhelmed, exposing inconsistencies."
        ),
        "steps": [
            {
                "step": 1,
                "title": "Locking the Forward Narrative",
                "objective": "Allow the subject to recite their rehearsed forward timeline without interference.",
                "guidance": (
                    "Let the subject present their chronological cover story. Pay close attention to rehearsed markers: "
                    "overly neat temporal sequencing, lack of spontaneous self-corrections, and uniform detail."
                ),
                "example_dialogue": (
                    "Start from 5:00 PM when the team left, and take me chronologically through everything you did until you logged off."
                ),
                "behavioral_cues_to_watch": (
                    "Note the speed and smoothness of the delivery. Fabricated narratives are often rehearsed as a sequential script."
                ),
                "pitfalls": (
                    "Interrupting the forward narrative before all temporal claims are firmly on the record."
                ),
            },
            {
                "step": 2,
                "title": "Reverse Chronological Interrogation",
                "objective": "Disrupt rehearsed scripts by asking the subject to recount events in reverse order.",
                "guidance": (
                    "Ask the subject to start from their final action and work backwards step by step. Truthful autobiographical "
                    "memory can easily navigate backward, whereas fabricated scripts impose severe cognitive strain."
                ),
                "example_dialogue": (
                    "Before you got in your car to drive away, what was the very last thing you touched in the office? "
                    "And right before that? Walk me backwards from your car back to the desk."
                ),
                "behavioral_cues_to_watch": (
                    "Significant latency increases, sudden loss of fluency, prolonged filler sounds ('um', 'ah'), "
                    "heavy sighing, and looking downward."
                ),
                "pitfalls": (
                    "Allowing the subject to turn around and reconstruct the story forward again."
                ),
            },
            {
                "step": 3,
                "title": "Unanticipated Sensory Probing",
                "objective": "Probe peripheral sensory details that an innocent person naturally encodes but a liar fails to plan.",
                "guidance": (
                    "Ask about ambient sounds, smells, lighting conditions, or physical sensations at critical moments. "
                    "Liars prepare facts and actions, rarely peripheral sensory context."
                ),
                "example_dialogue": (
                    "When you were standing by the petty cash drawer, was the radio in the reception area playing? "
                    "Did you hear the phone ringing while you had the key in the lock?"
                ),
                "behavioral_cues_to_watch": (
                    "Long hesitation while inventing sensory details, or contradictory sensory assertions."
                ),
                "pitfalls": (
                    "Asking leading sensory questions that hand the subject an easy answer."
                ),
            },
            {
                "step": 4,
                "title": "Spatial Diagramming and Action Mapping",
                "objective": "Require physical or spatial representation of the claims to test geometric logic.",
                "guidance": (
                    "Ask the subject to sketch the layout, trace their path on a floor plan, or physically demonstrate their movements. "
                    "Spatial reconstruction demands high cognitive effort and reveals impossible physical relationships."
                ),
                "example_dialogue": (
                    "Take this notepad and sketch where you were standing in the server room relative to the rack, the door, "
                    "and the camera. Mark your exact line of sight."
                ),
                "behavioral_cues_to_watch": (
                    "Hesitation when placing key objects, erasing or redrawing paths, or realizing their physical position "
                    "contradicts their earlier visual claims."
                ),
                "pitfalls": (
                    "Critiquing drawing ability rather than evaluating the spatial logic and temporal feasibility."
                ),
            },
        ],
    },
    "minimization_and_rationalization": {
        "id": "minimization_and_rationalization",
        "title": "Minimization, Rationalization, and Face-Saving",
        "category": "persuasion",
        "aliases": ["minimization", "rationalization", "face saving", "moral justification", "mitigation"],
        "overview": (
            "Subjects withhold the truth primarily out of fear of consequences and loss of self-respect. "
            "By providing face-saving themes, moral justifications, and reducing the perceived psychological cost "
            "of confessing, the interviewer encourages honest disclosure."
        ),
        "steps": [
            {
                "step": 1,
                "title": "Empathy and Psychological Normalization",
                "objective": "Lower emotional resistance by framing the incident as an understandable human reaction under pressure.",
                "guidance": (
                    "Acknowledge external stressors (workload, family emergency, awkward peer pressure) that could push "
                    "anyone into a poor decision. Never judge; establish warm, non-judgmental presence."
                ),
                "example_dialogue": (
                    "I understand how stressful things have been around here lately with the audits and staffing shortages. "
                    "When people are pushed to their limits, anyone can make a quick judgment call they wouldn't normally make."
                ),
                "behavioral_cues_to_watch": (
                    "Shoulders lowering, deep exhalations, moistening lips, and eye contact shifting from defensive to receptive."
                ),
                "pitfalls": (
                    "Sounding patronizing or insincere. If the empathy doesn't feel genuine, the subject will suspect a trap."
                ),
            },
            {
                "step": 2,
                "title": "Reframing Malice vs. Mistake",
                "objective": "Distinguish the subject's behavior from true criminal or malicious misconduct.",
                "guidance": (
                    "Contrast malicious wrongdoing with an honest lapse in judgment or an attempt to help someone else. "
                    "Show the subject that you see them as a fundamentally decent person."
                ),
                "example_dialogue": (
                    "There are people who go out of their way to steal or compromise security with bad intentions. "
                    "I don't believe for a second that you're one of those people. Doing a quick favor for a coworker is very different."
                ),
                "behavioral_cues_to_watch": (
                    "Head nodding, subtle verbal agreement ('Yeah', 'Exactly'), and lessening of physical barriers (uncrossing arms)."
                ),
                "pitfalls": (
                    "Making illegal or unauthorized promises of immunity or legal protection."
                ),
            },
            {
                "step": 3,
                "title": "The Face-Saving Binary Choice",
                "objective": "Offer a choice between a harsh, unacceptable motive and an understandable, face-saving motive.",
                "guidance": (
                    "Present two options: both acknowledge the act, but one preserves dignity while the other represents malice. "
                    "The subject naturally grasps the face-saving alternative."
                ),
                "example_dialogue": (
                    "Did you prop that door open to create a security vulnerability for the system, or was it just a split-second favor "
                    "for a friend that you meant to close right away?"
                ),
                "behavioral_cues_to_watch": (
                    "Rapid verbal adoption of the face-saving option: 'It was just a split second, I never meant to leave it open!'"
                ),
                "pitfalls": (
                    "Including an option that allows total denial, or pressing before rapport has been adequately built."
                ),
            },
            {
                "step": 4,
                "title": "Converting Admission to Full Truth",
                "objective": "Immediately follow up on the first admission to gather all concrete, verifiable facts.",
                "guidance": (
                    "Do not react with triumphant excitement. Stay calm, supportive, and immediately guide the subject "
                    "to provide specific names, times, and actions before second thoughts set in."
                ),
                "example_dialogue": (
                    "I respect your honesty in telling me that. Let's make sure we have all the details straight: who was the colleague, "
                    "and what time did they ask you for the badge pass?"
                ),
                "behavioral_cues_to_watch": (
                    "Uninhibited flow of detail, open body language, emotional catharsis."
                ),
                "pitfalls": (
                    "Changing tone to punitive or accusatory the second the subject admits to the act."
                ),
            },
        ],
    },
    "rapport_and_authority": {
        "id": "rapport_and_authority",
        "title": "Rapport Building and Authority Activation",
        "category": "rapport",
        "aliases": ["rapport", "authority", "authority pillars", "rapport building", "ght", "good human test"],
        "overview": (
            "Leveraging Chase Hughes's Authority Pillars (Competence, Likability, Authority, Trust) and the Good Human Test "
            "(GHT) to create deep compliance and genuine cooperation without hostility."
        ),
        "steps": [
            {
                "step": 1,
                "title": "Pacing and Attunement",
                "objective": "Establish subconscious harmony by matching speech rate, vocal tone, and posture.",
                "guidance": (
                    "Subtly align your energy and vocal tempo with the subject. Validate their feelings of discomfort "
                    "without validating false claims."
                ),
                "example_dialogue": (
                    "I recognize that being pulled into an unexpected meeting can feel uncomfortable. My goal is simply to get "
                    "clarity on what happened so you can get back to your regular work."
                ),
                "behavioral_cues_to_watch": (
                    "Breathing synchronization, posture mirroring, and subject speaking with less defensive edge."
                ),
                "pitfalls": (
                    "Mimicking movements too abruptly or obviously, which appears mocking or manipulative."
                ),
            },
            {
                "step": 2,
                "title": "Projecting Quiet Competence",
                "objective": "Demonstrate calm mastery of the situation so the subject realizes deception is futile.",
                "guidance": (
                    "Speak with measured cadence and stillness. Avoid unnecessary hand gestures, head tilting, or verbal fillers. "
                    "Know the key facts thoroughly."
                ),
                "example_dialogue": (
                    "I have the access logs, camera timestamps, and maintenance reports right here. I'm not guessing about the timeline; "
                    "I'm here to hear your side before writing my summary."
                ),
                "behavioral_cues_to_watch": (
                    "Subject sitting up straighter, abandoning casual or dismissive attitudes, taking the dialogue seriously."
                ),
                "pitfalls": (
                    "Arrogance or aggressive posturing, which destroys likability and trust."
                ),
            },
            {
                "step": 3,
                "title": "Activating the Good Human Test (GHT)",
                "objective": "Appeal to the subject's self-concept as an honest, responsible professional.",
                "guidance": (
                    "Affirm the subject's character, reputation, and core values. Position coming clean as the only choice "
                    "congruent with their personal integrity."
                ),
                "example_dialogue": (
                    "Everyone I've spoken to says you're reliable, thorough, and someone who takes pride in doing things right. "
                    "That's why I know you value integrity more than hiding behind an excuse."
                ),
                "behavioral_cues_to_watch": (
                    "Direct eye contact, earnest tone, chin lifting, and reduction in fidgeting."
                ),
                "pitfalls": (
                    "Laying on excessive or unearned praise, which sounds manipulative."
                ),
            },
        ],
    },
    "deception_detection_drs": {
        "id": "deception_detection_drs",
        "title": "Deception Tell Cluster Detection (DRS)",
        "category": "analysis",
        "aliases": ["deception", "drs", "deception rating scale", "btoe", "tells", "deception detection"],
        "overview": (
            "Systematic identification of deceptive indicators using the Deception Rating Scale (DRS) and Behavioral Table of Elements (BTOE). "
            "Teaches the Rule of Three: never evaluate deception on a single isolated tick, but only on clusters of 3+ indicators within 2 seconds."
        ),
        "steps": [
            {
                "step": 1,
                "title": "Applying the Rule of Three",
                "objective": "Isolate true deceptive clusters from ordinary nervous ticks.",
                "guidance": (
                    "When asking a stress question, observe the 2-second response window. Count whether at least three distinct "
                    "indicators (e.g. neck touch + gaze aversion + throat clearing) occur together."
                ),
                "example_dialogue": (
                    "Were you inside the server room at any point between 9:00 PM and midnight?"
                ),
                "behavioral_cues_to_watch": (
                    "Autonomic (swallowing, blushing), kinesic (pacifying, shielding), and verbal (hedging, stuttering) tells occurring simultaneously."
                ),
                "pitfalls": (
                    "Accusing someone of lying because of a single isolated nervous gesture like tapping a foot."
                ),
            },
            {
                "step": 2,
                "title": "Linguistic and Statement Analysis",
                "objective": "Identify verbal distancing, tense shifts, and unprompted qualifiers in speech.",
                "guidance": (
                    "Listen for pronoun drops ('Went to desk' instead of 'I went to my desk'), tense switching between past and present, "
                    "and excessive truth qualifiers ('to be completely honest', 'as God is my witness')."
                ),
                "example_dialogue": (
                    "Listen closely to how they phrase their denial: 'I would never do that' is a belief statement, not a factual denial like 'I did not do that'."
                ),
                "behavioral_cues_to_watch": (
                    "Unnecessary detail in non-critical periods coupled with sparse detail during the critical time window."
                ),
                "pitfalls": (
                    "Ignoring spoken grammar while fixating entirely on body language."
                ),
            },
            {
                "step": 3,
                "title": "Micro-Expressions and Facial Asymmetry",
                "objective": "Detect fleeting involuntary emotional leakage on the face.",
                "guidance": (
                    "Watch for involuntary facial movements lasting 1/25th to 1/5th of a second. Look for asymmetrical expressions, "
                    "especially unilateral lip-corner raises (duping delight or contempt)."
                ),
                "example_dialogue": (
                    "Notice the split second after you ask the critical question before their conscious mask is applied."
                ),
                "behavioral_cues_to_watch": (
                    "Unilateral smirks, brief brow furrowing, lip compression, or rapid micro-blinking."
                ),
                "pitfalls": (
                    "Expecting micro-expressions to be sustained; they are fleeting and require focused visual attention."
                ),
            },
            {
                "step": 4,
                "title": "Targeted Factual Verification",
                "objective": "Directly cross-examine behavioral hot spots with verifiable external facts.",
                "guidance": (
                    "Take the points in the story that triggered the strongest DRS cluster and probe for hard, verifiable details "
                    "(names, timestamps, serial numbers) that can be audited."
                ),
                "example_dialogue": (
                    "You said you were speaking with someone in the hallway at that moment. What is their full name and department?"
                ),
                "behavioral_cues_to_watch": (
                    "Vagueness or sudden memory loss on verifiable specifics compared to sharp memory on unverifiable details."
                ),
                "pitfalls": (
                    "Concluding an investigation based solely on behavioral reads without securing objective evidence."
                ),
            },
        ],
    },
}


def normalize_technique_name(name: str) -> str:
    """Normalizes a technique name query to match catalog keys."""
    if not name:
        return ""
    cleaned = name.lower().strip().replace("-", "_").replace(" ", "_")
    if not cleaned:
        return ""
    if cleaned in TECHNIQUES:
        return cleaned

    for tech_id, data in TECHNIQUES.items():
        if cleaned in tech_id:
            return tech_id
        for alias in data.get("aliases", []):
            alias_clean = alias.lower().strip().replace("-", "_").replace(" ", "_")
            if cleaned == alias_clean or cleaned in alias_clean or alias_clean in cleaned:
                return tech_id

    return ""


def list_techniques() -> list[dict[str, Any]]:
    """Returns a summary catalog of all available techniques."""
    summaries = []
    for tech in TECHNIQUES.values():
        summaries.append({
            "id": tech["id"],
            "title": tech["title"],
            "category": tech["category"],
            "overview": tech["overview"],
            "total_steps": len(tech["steps"]),
        })
    return summaries


def get_technique_step(technique_name: str, step: int = 1) -> dict[str, Any]:
    """Retrieves a specific step for a technique, or catalog if not found."""
    canonical_id = normalize_technique_name(technique_name)
    if not canonical_id or canonical_id not in TECHNIQUES:
        return {
            "status": "technique_not_found" if technique_name else "catalog",
            "requested": technique_name,
            "message": (
                f"Technique {technique_name!r} not found. Please choose from available techniques."
                if technique_name
                else "Available interviewing techniques catalog:"
            ),
            "available_techniques": list_techniques(),
        }

    tech = TECHNIQUES[canonical_id]
    steps: list[dict[str, Any]] = tech["steps"]
    total_steps = len(steps)

    if step <= 0:
        step = 1

    if step > total_steps:
        return {
            "status": "technique_completed",
            "technique_id": canonical_id,
            "title": tech["title"],
            "total_steps": total_steps,
            "message": (
                f"You have completed all {total_steps} steps of {tech['title']}! "
                "You can now practice this technique in a drill (call start_sprint or reverse_roles), "
                "or choose another technique to learn."
            ),
        }

    step_data = steps[step - 1]
    is_last = (step == total_steps)
    next_step = None if is_last else step + 1

    return {
        "status": "ok",
        "technique_id": canonical_id,
        "title": tech["title"],
        "category": tech["category"],
        "overview": tech["overview"],
        "step": step,
        "total_steps": total_steps,
        "step_title": step_data["title"],
        "objective": step_data["objective"],
        "guidance": step_data["guidance"],
        "example_dialogue": step_data["example_dialogue"],
        "behavioral_cues_to_watch": step_data["behavioral_cues_to_watch"],
        "pitfalls": step_data["pitfalls"],
        "next_step": next_step,
        "is_last_step": is_last,
    }
