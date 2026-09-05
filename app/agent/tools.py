"""ADK tools for the interrogation-drill trainer.

Two tools:
  - start_sprint: game-master tool that picks a fictional scenario and hands
    its full data (including the hidden truth) to the model's own context so
    it can role-play consistently — the SYSTEM INSTRUCTION is what keeps the
    hidden truth out of the model's spoken output until debrief, not this tool.
  - query_knowledge_base: hybrid retrieval over the indexed reference material,
    used only during debrief per the system instruction.
"""

from __future__ import annotations

import logging
import random
from typing import Any, Callable

from google.adk.tools import ToolContext

from app.agent.persona import SCENARIOS, DrillScenario, get_scenario, list_scenarios

logger = logging.getLogger("interrogation_drill.tools")

_USED_SCENARIOS_KEY = "used_scenario_ids"


def start_sprint(
    scenario_id: str = "",
    difficulty: str = "",
    tool_context: ToolContext | None = None,
) -> dict:
    """Starts a new fictional interrogation drill sprint.

    Call this once at the start of each sprint, before switching into character.
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

        Only use this during the DEBRIEF phase, to ground feedback in the real
        Behavioral Table of Elements / Deception Rating Scale / Authority
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
