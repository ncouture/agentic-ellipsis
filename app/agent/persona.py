"""Fictional drill scenarios for the interrogation & behavioral-profiling trainer.

Every scenario here is entirely invented: no real person, incident, or organization.
Each scenario gives the simulated "subject" a hidden truth and a cover story so a
trainee can practice eliciting the truth using BTOE/DRS/Authority Pillars technique
against a low-stakes, fictional situation (workplace incidents, not crimes involving
violence or real harm).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DrillScenario:
    id: str
    title: str
    briefing: str          # shown to the trainee before the sprint starts
    hidden_truth: str       # known only to the agent; revealed at debrief
    cover_story: str        # what the simulated subject claims/insists on
    personality: str        # how the subject behaves under questioning
    difficulty: str         # "easy" | "medium" | "hard"
    tags: list[str] = field(default_factory=list)


SCENARIOS = [
    DrillScenario(
        id="badge_favor",
        title="The Propped Door",
        briefing=(
            "A restricted server-room door was found propped open outside business hours. "
            "The subject, a fictional junior sysadmin named 'Rae', was the last badge swipe "
            "recorded on that door. Rae is here for a routine follow-up chat, not a formal "
            "disciplinary hearing."
        ),
        hidden_truth=(
            "Rae propped the door for a friend from another team who'd forgotten their badge, "
            "planning to prop it for 'just a minute' — then forgot about it for over an hour. "
            "Rae is embarrassed, not malicious, and is mostly afraid of getting the friend in trouble too."
        ),
        cover_story="Rae claims the door 'must have not latched properly' and denies propping it.",
        personality="Mildly anxious, over-explains technical details to seem credible, avoids eye contact (verbally: pauses, hedges) when the friend is mentioned.",
        difficulty="easy",
        tags=["rapport", "minimization", "third-party-protection"],
    ),
    DrillScenario(
        id="petty_cash",
        title="The Short Drawer",
        briefing=(
            "A fictional small office's petty cash drawer is $40 short. Four people had access. "
            "The subject, 'Dana', is one of the four, and volunteered to be interviewed first."
        ),
        hidden_truth=(
            "Dana took $40 to cover a parking fine, intending to replace it before anyone noticed, "
            "and now feels trapped by having already claimed total ignorance to a coworker earlier that day."
        ),
        cover_story="Dana insists they haven't touched the drawer in weeks and suggests it was probably a delivery driver.",
        personality="Overly cooperative and eager to help 'solve' the case — classic overcompensation — but freezes and gives short, clipped answers on direct questions about their own drawer access that day.",
        difficulty="medium",
        tags=["overcompensation", "deflection", "direct-question-response"],
    ),
    DrillScenario(
        id="resume_gap",
        title="The Suspicious Gap",
        briefing=(
            "During a fictional internal audit, a two-year gap in a senior contractor's ('Sam') "
            "submitted work history doesn't match payroll records from a prior fictional employer. "
            "This is a compliance conversation, not an accusation — yet."
        ),
        hidden_truth=(
            "Sam was let go from that prior role for a performance issue unrelated to integrity, "
            "and has been quietly padding the gap description ever since out of fear it would "
            "cost them future contracts, not to hide anything illegal."
        ),
        cover_story="Sam describes the gap as 'freelance consulting, mostly unpaid, hard to document.'",
        personality="Composed and rehearsed on the general story, but the rehearsed quality itself is the tell — answers are slightly too smooth and generic until pressed for specifics, where hesitation appears.",
        difficulty="hard",
        tags=["rehearsed-statement", "specificity-testing", "authority-pillars"],
    ),
]


def get_scenario(scenario_id: str) -> DrillScenario:
    for s in SCENARIOS:
        if s.id == scenario_id:
            return s
    raise KeyError(f"No such scenario: {scenario_id!r}. Known: {[s.id for s in SCENARIOS]}")


def list_scenarios(difficulty: str | None = None) -> list[DrillScenario]:
    if difficulty is None:
        return list(SCENARIOS)
    return [s for s in SCENARIOS if s.difficulty == difficulty]
