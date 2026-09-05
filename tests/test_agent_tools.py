from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from app.agent.persona import SCENARIOS, DrillScenario, get_scenario, list_scenarios
from app.agent.tools import start_sprint, make_query_knowledge_base_tool
from app.agent.instruction import build_system_instruction


def test_persona_scenarios_listing():
    all_scenarios = list_scenarios()
    assert len(all_scenarios) == 3
    assert set(s.id for s in all_scenarios) == {"badge_favor", "petty_cash", "resume_gap"}

    easy = list_scenarios("easy")
    assert len(easy) == 1
    assert easy[0].id == "badge_favor"

    scenario = get_scenario("petty_cash")
    assert scenario.title == "The Short Drawer"
    assert "parking fine" in scenario.hidden_truth

    with pytest.raises(KeyError):
        get_scenario("non_existent")


def test_start_sprint_explicit_scenario():
    res = start_sprint(scenario_id="badge_favor")
    assert res["scenario_id"] == "badge_favor"
    assert res["difficulty"] == "easy"
    assert "restricted server-room" in res["briefing"].lower()


def test_start_sprint_with_tool_context_session_isolation():
    class DummyContext:
        def __init__(self):
            self.state = {}

    ctx1 = DummyContext()
    ctx2 = DummyContext()

    res1 = start_sprint(tool_context=ctx1)
    assert len(ctx1.state["used_scenario_ids"]) == 1
    assert ctx2.state == {}

    res2 = start_sprint(tool_context=ctx2)
    assert len(ctx2.state["used_scenario_ids"]) == 1


def test_query_knowledge_base_tool_empty_results():
    mock_bm25 = MagicMock()
    mock_chroma = MagicMock()
    mock_chroma.query.return_value = {"ids": [[]]}
    mock_bm25.get_scores.return_value = []

    query_kb = make_query_knowledge_base_tool(
        bm25_index=mock_bm25,
        bm25_ids=[],
        chroma_collection=mock_chroma,
    )
    res = query_kb("nonexistent term")
    assert res == "No specific data found in documentation."


def test_instruction_assembly():
    instruction = build_system_instruction("Test Outline Section")
    assert "VOICE & PACING" in instruction
    assert "GAME STRUCTURE: BRIEFING -> IN-CHARACTER -> DEBRIEF" in instruction
    assert "SCOPE BOUNDARY" in instruction
    assert "Test Outline Section" in instruction
