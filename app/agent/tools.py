"""ADK tools for the interrogation-drill trainer.

Tools:
  - start_sprint: game-master tool that picks a fictional scenario where trainee
    interviews the agent (agent plays the subject).
  - reverse_roles: reverses roles so the trainee plays the subject defending a
    cover story, and the agent acts as the interviewer demonstrating professional
    elicitation techniques.
  - teach_interviewing_technique: teaches step-by-step interviewing and interrogation
    techniques with clear objectives, examples, behavioral tell detection, and pitfalls.
  - query_knowledge_base: hybrid retrieval over the indexed reference material,
    used during debrief or teaching per system instructions.
"""

from __future__ import annotations

import logging
import random
import re
from typing import Any, Callable

from google.adk.tools import ToolContext

from app.agent.persona import (
    DUAL_TRACK_BRIEFS,
    DrillScenario,
    DualTrackBrief,
    SCENARIOS,
    get_dual_track_brief,
    get_scenario,
    list_dual_track_briefs,
    list_scenarios,
)
from app.agent.techniques import (
    TECHNIQUES,
    get_technique_step,
    list_techniques,
    normalize_technique_name,
)

logger = logging.getLogger("interrogation_drill.tools")

_USED_SCENARIOS_KEY = "used_scenario_ids"

_KNOWN_CHARACTER_NAMES: dict[str, str] = {
    "badge_favor": "Rae",
    "petty_cash": "Dana",
    "resume_gap": "Sam",
}


def _extract_character_name(scenario: DrillScenario) -> str:
    if scenario.id in _KNOWN_CHARACTER_NAMES:
        return _KNOWN_CHARACTER_NAMES[scenario.id]
    match = re.search(r"['\"]([A-Z][a-z]+)['\"]", scenario.briefing)
    if match:
        return match.group(1)
    return "the subject"


def start_sprint(
    scenario_id: str = "",
    difficulty: str = "",
    tool_context: ToolContext | None = None,
) -> dict:
    """Starts a new fictional interrogation drill sprint where trainee is the interviewer.

    Call this once at the start of each standard sprint, before switching into character.
    Args:
        scenario_id: Exact id of a scenario to run (see list_scenarios). Leave
            empty to pick one at random.
        difficulty: "easy", "medium", or "hard" — used only when scenario_id is
            empty, to filter the random pick. Leave empty for any difficulty.
    Returns:
        A dict with the full scenario data: briefing (speak this to the
        trainee), hidden_truth and cover_story and personality (keep these out
        of your spoken output until the debrief phase per your instructions).
    """
    used_ids: set[str] = set()
    if tool_context is not None and tool_context.state is not None:
        used_ids = set(tool_context.state.get(_USED_SCENARIOS_KEY, []))

    if scenario_id:
        scenario = get_scenario(scenario_id)
    else:
        pool = list_scenarios(difficulty or None) or list(SCENARIOS)
        unused = [s for s in pool if s.id not in used_ids] or pool
        scenario = random.choice(unused)

    used_ids.add(scenario.id)
    if tool_context is not None and tool_context.state is not None:
        tool_context.state[_USED_SCENARIOS_KEY] = list(used_ids)
        tool_context.state["active_role"] = "interviewee"
        tool_context.state["active_scenario_id"] = scenario.id

    logger.info("Sprint started: %s (difficulty=%s)", scenario.id, scenario.difficulty)
    return {
        "scenario_id": scenario.id,
        "title": scenario.title,
        "briefing": scenario.briefing,
        "hidden_truth": scenario.hidden_truth,
        "cover_story": scenario.cover_story,
        "personality": scenario.personality,
        "difficulty": scenario.difficulty,
    }


def reverse_roles(
    scenario_id: str = "",
    difficulty: str = "",
    tool_context: ToolContext | None = None,
) -> dict:
    """Reverses roles so the agent becomes the interviewer and the trainee becomes the interviewee.

    Call this when starting a reverse-role sprint where the trainee practices being
    questioned while defending a cover story and hiding a secret truth, and the agent
    demonstrates professional interviewing, baseline calibration, and elicitation techniques.

    Args:
        scenario_id: Exact id of a scenario to run (see list_scenarios). Leave
            empty to pick one at random.
        difficulty: "easy", "medium", or "hard" — used only when scenario_id is
            empty, to filter the random pick. Leave empty for any difficulty.
    Returns:
        A dict with role reversal details:
        - mode: "reverse_roles"
        - scenario_id: The selected scenario ID
        - title: Scenario title
        - briefing: Overview of the incident
        - trainee_role: Instructions for the trainee (character name, cover story,
          hidden truth to defend, and setup prompt)
        - interviewer_guide: Guide for the agent on target truths, key tells to probe,
          and questioning strategy
        - difficulty: Scenario difficulty
    """
    used_ids: set[str] = set()
    if tool_context is not None and tool_context.state is not None:
        used_ids = set(tool_context.state.get(_USED_SCENARIOS_KEY, []))

    if scenario_id:
        scenario = get_scenario(scenario_id)
    else:
        pool = list_scenarios(difficulty or None) or list(SCENARIOS)
        unused = [s for s in pool if s.id not in used_ids] or pool
        scenario = random.choice(unused)

    used_ids.add(scenario.id)
    character_name = _extract_character_name(scenario)

    if tool_context is not None and tool_context.state is not None:
        tool_context.state[_USED_SCENARIOS_KEY] = list(used_ids)
        tool_context.state["active_role"] = "interviewer"
        tool_context.state["active_scenario_id"] = scenario.id

    logger.info("Reverse-role sprint started: %s (difficulty=%s)", scenario.id, scenario.difficulty)

    instructions_to_speak = (
        f"We're reversing roles! You will be the subject, and I will be interviewing you. "
        f"You are playing {character_name}. Background: {scenario.briefing} "
        f"Your cover story: {scenario.cover_story} "
        f"Your secret to protect: {scenario.hidden_truth} "
        f"Try to stay composed and defend your cover story. Let me know when you are ready to begin."
    )

    return {
        "mode": "reverse_roles",
        "scenario_id": scenario.id,
        "title": scenario.title,
        "difficulty": scenario.difficulty,
        "briefing": scenario.briefing,
        "hidden_truth": scenario.hidden_truth,
        "cover_story": scenario.cover_story,
        "trainee_role": {
            "character_name": character_name,
            "briefing": scenario.briefing,
            "cover_story": scenario.cover_story,
            "hidden_truth": scenario.hidden_truth,
            "instructions_to_speak_to_trainee": instructions_to_speak,
        },
        "interviewer_guide": {
            "role": "interviewer",
            "subject_name": character_name,
            "target_truth_to_uncover": scenario.hidden_truth,
            "subject_claimed_cover_story": scenario.cover_story,
            "vulnerabilities_and_tells": scenario.personality,
            "recommended_strategy": (
                "1. Start with neutral baseline questions to establish normal demeanor. "
                "2. Use broad open questions to get their timeline. "
                "3. Apply cognitive load (e.g. reverse timeline or sensory details) to test consistency. "
                "4. Introduce empathy and face-saving minimization to elicit the truth."
            ),
        },
    }


# Alias for reverse_roles
start_reverse_sprint = reverse_roles


def teach_interviewing_technique(
    technique_name: str = "",
    step: int = 1,
    tool_context: ToolContext | None = None,
) -> dict:
    """Teaches step-by-step interviewing, elicitation, and behavioral profiling techniques.

    Call this tool to guide the trainee through structured, step-by-step lessons on
    funnel questioning, baseline norming, cognitive load induction, minimization,
    rapport/authority activation, or deception tell detection.

    Args:
        technique_name: Name of the technique to learn (e.g. "funnel_method",
            "baseline_and_norming", "cognitive_load", "minimization_and_rationalization",
            "rapport_and_authority", "deception_detection_drs"). Leave empty to list
            all available techniques.
        step: Step number to retrieve (1-indexed). Defaults to 1.
    Returns:
        A dict containing either the list of available techniques (if technique_name is
        empty or unknown) or the specific lesson step details: title, objective, actionable
        guidance, example dialogue to speak, behavioral cues to watch for, common pitfalls,
        and pointer to the next step.
    """
    result = get_technique_step(technique_name, step=step)

    if tool_context is not None and tool_context.state is not None:
        if result.get("status") == "ok":
            tool_context.state["current_technique"] = result.get("technique_id")
            tool_context.state["current_step"] = step

    logger.info(
        "teach_interviewing_technique called: requested=%r step=%d status=%s",
        technique_name, step, result.get("status"),
    )
    return result


# Alias for teach_interviewing_technique
teach_technique = teach_interviewing_technique


def start_whisper_drill(
    scenario_id: str = "",
    difficulty: str = "",
    tool_context: ToolContext | None = None,
) -> dict:
    """Starts a dual-track over-the-phone interview drill with real-time technique coaching.

    The agent operates as both:
    1. In-Character Interrogator/Interviewer: Conducting a dynamic over-the-phone
       investigative interview against the trainee's assigned fictional brief.
    2. Out-of-Character Technique Coach: Stepping out of character with the distinct
       tag `[COACH DEBRIEF]` to whisper tactical mechanics (strategic silence,
       vacuum elicitation, baseline mapping, presumptive assertions, timeline challenges)
       in real time.

    Args:
        scenario_id: Exact id of a scenario brief (e.g. "audit_ledger", "badge_favor",
            "petty_cash", "resume_gap"). Leave empty to pick one.
        difficulty: "easy", "medium", or "hard" to filter if scenario_id is empty.
    Returns:
        A dict containing:
        - mode: "dual_track_whisper"
        - scenario_id: The selected scenario ID
        - title: Scenario title
        - difficulty: Scenario difficulty
        - trainee_brief: Fictional role, open knowledge, restricted facts, objective,
          stress points, and instructions to speak to trainee in Phase 1.
        - interviewer_protocol: Guidelines for Phase 2 phone interview and Phase 3
          tactical coaching callouts.
    """
    used_ids: set[str] = set()
    if tool_context is not None and tool_context.state is not None:
        used_ids = set(tool_context.state.get(_USED_SCENARIOS_KEY, []))

    if scenario_id:
        brief = get_dual_track_brief(scenario_id)
    else:
        pool = list_dual_track_briefs(difficulty or None) or list(DUAL_TRACK_BRIEFS.values())
        unused = [b for b in pool if b.scenario_id not in used_ids] or pool
        brief = random.choice(unused)

    used_ids.add(brief.scenario_id)
    if tool_context is not None and tool_context.state is not None:
        tool_context.state[_USED_SCENARIOS_KEY] = list(used_ids)
        tool_context.state["active_role"] = "interviewer_and_coach"
        tool_context.state["active_mode"] = "dual_track_whisper"
        tool_context.state["active_scenario_id"] = brief.scenario_id

    logger.info("Dual-track whisper drill started: %s (difficulty=%s)", brief.scenario_id, brief.difficulty)

    instructions_to_speak = (
        f"Welcome to the dual-track over-the-phone drill. Here is your fictional brief: "
        f"You are the {brief.role}. "
        f"Your objective: {brief.objective} "
        f"Open knowledge you can freely share: {'; '.join(brief.open_knowledge)}. "
        f"Restricted facts to safeguard: {'; '.join(brief.restricted_facts)}. "
        f"I will dial in as a lead investigator for a realistic phone interview. "
        f"Throughout the drill, I will periodically step out of character using the tag "
        f"'[COACH DEBRIEF]' to whisper behind-the-curtain tactical insights into your ear. "
        f"Let me know when you are ready to connect the call."
    )

    return {
        "mode": "dual_track_whisper",
        "scenario_id": brief.scenario_id,
        "title": brief.title,
        "difficulty": brief.difficulty,
        "trainee_brief": {
            "role": brief.role,
            "open_knowledge": brief.open_knowledge,
            "restricted_facts": brief.restricted_facts,
            "objective": brief.objective,
            "stress_points": brief.stress_points,
            "instructions_to_speak_to_trainee": instructions_to_speak,
        },
        "interviewer_protocol": {
            "role": "investigator",
            "call_format": "over-the-phone",
            "baseline_mapping": (
                "Start with low-stakes, neutral questions (e.g. confirming office location, "
                "tenure, routine operations) to assess baseline cadence, filler words, and vocal tension."
            ),
            "strategic_pacing": (
                "Leave deliberate dead air (3-5 seconds of silence) after the trainee speaks. "
                "Test comfort with silence and impulse to over-explain (vacuum elicitation)."
            ),
            "tactical_pivots": [
                "Open elicitation: Ask broad questions to get unscripted narrative.",
                "Presumptive assertions: Frame statements with assumed facts ('When you saw the updated ledger...') to elicit corrections.",
                "Timeline challenges: Sudden chronological jumps or sensory detail requests to test cognitive load.",
            ],
            "coach_tag": "[COACH DEBRIEF]",
            "tactical_callout_instructions": (
                "Briefly step out of character using '[COACH DEBRIEF]' to explain the technique just deployed "
                "in real time (e.g. vacuum elicitation, baseline shift, presumptive questioning), then cleanly "
                "resume the call."
            ),
        },
    }


# Aliases for start_whisper_drill
start_dual_track_drill = start_whisper_drill
start_phone_interview_drill = start_whisper_drill


def make_query_knowledge_base_tool(
    bm25_index: Any,
    bm25_ids: list[str],
    chroma_collection: Any,
    top_k: int = 2,
) -> Callable[[str, str], str]:
    """Builds the query_knowledge_base tool bound to a specific retrieval index.

    Kept as a factory (rather than a bare module-level function) because the
    tool needs live handles to the loaded BM25 index and Chroma collection,
    which main.py constructs at startup via app.scripts.warmup.warm_up.
    """
    from app.retrieval.hybrid import hybrid_search

    def query_knowledge_base(query: str, topic_filter: str = "") -> str:
        """Looks up a fact or definition in the indexed reference material.

        Only use this during the DEBRIEF phase or when teaching theory, to ground feedback
        in the real Behavioral Table of Elements / Deception Rating Scale / Authority
        Pillars / Ellipsis Dialogue material.

        Args:
            query: A focused question or term to look up.
            topic_filter: Optional document or section name to narrow the
                search, if you can identify one from the reference outline.
        Returns:
            A short plain-text passage with its source, or a message saying
            nothing relevant was found. Under 150 words.
        """
        search_query = f"{topic_filter}: {query}" if topic_filter else query
        try:
            results = hybrid_search(search_query, bm25_index, bm25_ids, chroma_collection, top_k=top_k)
        except Exception:
            logger.exception("query_knowledge_base retrieval failed")
            return "No specific data found in documentation."

        if not results:
            return "No specific data found in documentation."

        parts = []
        for r in results:
            meta = r.get("metadata", {}) or {}
            source = meta.get("document_name", "reference material")
            section = meta.get("section_title", "")
            label = f"{source} ({section})" if section else source
            parts.append(f"Source ({label}): {r.get('text', '').strip()}")
        combined = "\n".join(parts)
        words = combined.split()
        if len(words) > 150:
            combined = " ".join(words[:150]) + "..."
        return combined

    return query_knowledge_base
