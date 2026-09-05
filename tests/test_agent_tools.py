from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from app.agent.persona import SCENARIOS, DrillScenario, get_scenario, list_scenarios
from app.agent.tools import (
    start_sprint,
    reverse_roles,
    start_reverse_sprint,
    teach_interviewing_technique,
    teach_technique,
    make_query_knowledge_base_tool,
)
from app.agent.techniques import list_techniques, normalize_technique_name, get_technique_step
from app.agent.instruction import build_system_instruction
from app.agent.agent import build_root_agent


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
    assert ctx1.state["active_role"] == "interviewee"
    assert ctx2.state == {}

    res2 = start_sprint(tool_context=ctx2)
    assert len(ctx2.state["used_scenario_ids"]) == 1


def test_reverse_roles_explicit_scenario():
    res = reverse_roles(scenario_id="badge_favor")
    assert res["mode"] == "reverse_roles"
    assert res["scenario_id"] == "badge_favor"
    assert res["difficulty"] == "easy"
    assert res["trainee_role"]["character_name"] == "Rae"
    assert "friend" in res["hidden_truth"].lower()
    assert "latch" in res["cover_story"].lower()
    assert "interviewer_guide" in res
    assert res["interviewer_guide"]["role"] == "interviewer"
    assert "Rae" in res["interviewer_guide"]["subject_name"]
    assert "Rae" in res["trainee_role"]["instructions_to_speak_to_trainee"]


def test_reverse_roles_difficulty_filter_and_alias():
    res_easy = reverse_roles(difficulty="easy")
    assert res_easy["scenario_id"] == "badge_favor"

    # Test alias
    res_alias = start_reverse_sprint(scenario_id="petty_cash")
    assert res_alias["scenario_id"] == "petty_cash"
    assert res_alias["trainee_role"]["character_name"] == "Dana"


def test_reverse_roles_with_tool_context_session_isolation():
    class DummyContext:
        def __init__(self):
            self.state = {}

    ctx = DummyContext()
    res = reverse_roles(scenario_id="resume_gap", tool_context=ctx)
    assert ctx.state["active_role"] == "interviewer"
    assert ctx.state["active_scenario_id"] == "resume_gap"
    assert "resume_gap" in ctx.state["used_scenario_ids"]


def test_teach_interviewing_technique_list_catalog():
    # Empty query returns catalog
    res = teach_interviewing_technique("")
    assert res["status"] == "catalog"
    assert len(res["available_techniques"]) >= 5
    ids = [t["id"] for t in res["available_techniques"]]
    assert "funnel_method" in ids
    assert "baseline_and_norming" in ids
    assert "cognitive_load" in ids
    assert "minimization_and_rationalization" in ids
    assert "rapport_and_authority" in ids
    assert "deception_detection_drs" in ids


def test_teach_interviewing_technique_step_progression():
    # Step 1
    step1 = teach_interviewing_technique("funnel_method", step=1)
    assert step1["status"] == "ok"
    assert step1["step"] == 1
    assert step1["total_steps"] == 4
    assert step1["next_step"] == 2
    assert not step1["is_last_step"]
    assert "example_dialogue" in step1
    assert "pitfalls" in step1

    # Step 4 (last step)
    step4 = teach_interviewing_technique("funnel_method", step=4)
    assert step4["status"] == "ok"
    assert step4["step"] == 4
    assert step4["next_step"] is None
    assert step4["is_last_step"]

    # Step past max
    completed = teach_interviewing_technique("funnel_method", step=5)
    assert completed["status"] == "technique_completed"
    assert "completed all" in completed["message"].lower()


def test_teach_interviewing_technique_fuzzy_names_and_alias():
    # Alias teach_technique
    res_alias = teach_technique("funnel", step=1)
    assert res_alias["technique_id"] == "funnel_method"

    # Fuzzy matching variations
    res_cog = teach_interviewing_technique("cognitive load", step=2)
    assert res_cog["technique_id"] == "cognitive_load"
    assert res_cog["step"] == 2

    res_norm = teach_interviewing_technique("baseline", step=1)
    assert res_norm["technique_id"] == "baseline_and_norming"

    res_drs = teach_interviewing_technique("drs", step=1)
    assert res_drs["technique_id"] == "deception_detection_drs"


def test_teach_interviewing_technique_tool_context_tracking():
    class DummyContext:
        def __init__(self):
            self.state = {}

    ctx = DummyContext()
    res = teach_interviewing_technique("cognitive_load", step=2, tool_context=ctx)
    assert res["status"] == "ok"
    assert ctx.state["current_technique"] == "cognitive_load"
    assert ctx.state["current_step"] == 2


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
    assert "REVERSE-ROLE SPRINT" in instruction
    assert "STEP-BY-STEP TECHNIQUE LESSONS" in instruction
    assert "DUAL-TRACK OVER-THE-PHONE DRILL" in instruction
    assert "[COACH DEBRIEF]" in instruction
    assert "SCOPE BOUNDARY & SAFETY GUARDRAILS" in instruction
    assert "SYNTHETIC IDENTITY ONLY" in instruction
    assert "CLOSED-LOOP SANDBOX" in instruction
    assert "Test Outline Section" in instruction


def test_root_agent_tools_configured():
    agent = build_root_agent()
    tool_names = [getattr(t, "__name__", str(t)) for t in agent.tools]
    assert "start_sprint" in tool_names
    assert "reverse_roles" in tool_names
    assert "teach_interviewing_technique" in tool_names
    assert "start_whisper_drill" in tool_names


def test_dual_track_briefs_listing():
    from app.agent.persona import list_dual_track_briefs, get_dual_track_brief
    briefs = list_dual_track_briefs()
    assert len(briefs) >= 4
    scenario_ids = [b.scenario_id for b in briefs]
    assert "audit_ledger" in scenario_ids
    assert "badge_favor" in scenario_ids
    assert "petty_cash" in scenario_ids
    assert "resume_gap" in scenario_ids

    brief = get_dual_track_brief("audit_ledger")
    assert "Corporate Controller" in brief.role
    assert len(brief.open_knowledge) > 0
    assert len(brief.restricted_facts) > 0
    assert brief.objective

    with pytest.raises(KeyError):
        get_dual_track_brief("non_existent_id")


def test_start_whisper_drill_explicit_scenario():
    from app.agent.tools import start_whisper_drill, start_dual_track_drill, start_phone_interview_drill
    res = start_whisper_drill(scenario_id="audit_ledger")
    assert res["mode"] == "dual_track_whisper"
    assert res["scenario_id"] == "audit_ledger"
    assert "trainee_brief" in res
    assert "Corporate Controller" in res["trainee_brief"]["role"]
    assert len(res["trainee_brief"]["open_knowledge"]) > 0
    assert len(res["trainee_brief"]["restricted_facts"]) > 0
    assert "instructions_to_speak_to_trainee" in res["trainee_brief"]
    assert "[COACH DEBRIEF]" in res["trainee_brief"]["instructions_to_speak_to_trainee"]

    # Protocol checks
    protocol = res["interviewer_protocol"]
    assert protocol["role"] == "investigator"
    assert protocol["coach_tag"] == "[COACH DEBRIEF]"
    assert "strategic_pacing" in protocol
    assert len(protocol["tactical_pivots"]) >= 3

    # Test aliases
    res_alias1 = start_dual_track_drill(scenario_id="badge_favor")
    assert res_alias1["scenario_id"] == "badge_favor"
    assert res_alias1["mode"] == "dual_track_whisper"

    res_alias2 = start_phone_interview_drill(scenario_id="petty_cash")
    assert res_alias2["scenario_id"] == "petty_cash"
    assert res_alias2["mode"] == "dual_track_whisper"


def test_start_whisper_drill_with_tool_context():
    from app.agent.tools import start_whisper_drill
    class DummyContext:
        def __init__(self):
            self.state = {}

    ctx = DummyContext()
    res = start_whisper_drill(scenario_id="audit_ledger", tool_context=ctx)
    assert ctx.state["active_role"] == "interviewer_and_coach"
    assert ctx.state["active_mode"] == "dual_track_whisper"
    assert ctx.state["active_scenario_id"] == "audit_ledger"
    assert "audit_ledger" in ctx.state["used_scenario_ids"]

