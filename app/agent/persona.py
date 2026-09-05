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


@dataclass(frozen=True)
class DualTrackBrief:
    scenario_id: str
    title: str
    role: str                       # Title, department, relation to scenario
    open_knowledge: list[str]       # Facts trainee is free to share
    restricted_facts: list[str]     # Information trainee must safeguard or negotiate carefully
    objective: str                  # Fictional goal
    stress_points: list[str] = field(default_factory=list) # Stress points/vulnerabilities
    difficulty: str = "medium"


DUAL_TRACK_BRIEFS: dict[str, DualTrackBrief] = {
    "audit_ledger": DualTrackBrief(
        scenario_id="audit_ledger",
        title="The Accelerated Disbursement",
        role="Corporate Controller, Finance Operations",
        open_knowledge=[
            "Quarterly account reconciliations were completed on time and verified.",
            "Standard accounts payable batch processing follows established internal controls.",
            "Vendor payments are categorized according to the standard chart of accounts.",
        ],
        restricted_facts=[
            "An off-cycle payment was expedited for an enterprise software vendor without the mandatory second VP signature due to executive pressure.",
            "The supporting documentation and authorization log were backfilled 48 hours after payment release.",
            "The vendor representative is a personal contact of a senior company officer.",
        ],
        objective="Cooperate with the internal audit inquiry, defend legitimate financial workflows, de-escalate auditor suspicion, and withhold sensitive board-level deliberations ethically without falsifying statements.",
        stress_points=[
            "Direct inquiry into missing authorization timestamps.",
            "Presumptive questions about vendor onboarding relationships.",
            "Strategic silence after explaining transaction approval flows.",
        ],
        difficulty="medium",
    ),
    "badge_favor": DualTrackBrief(
        scenario_id="badge_favor",
        title="The Propped Door",
        role="Junior System Administrator, IT Operations",
        open_knowledge=[
            "You worked an overtime maintenance shift on scheduled server patching.",
            "You swiped your badge to enter the server room at 8:00 PM.",
            "You verified server rack status and hardware temperatures during the shift.",
        ],
        restricted_facts=[
            "You propped the secure door open with a doorstop for a coworker from another team who left their badge at home.",
            "You meant to close it within minutes but forgot about it for over an hour.",
            "You have not informed management or security about the policy breach.",
        ],
        objective="Acknowledge legitimate maintenance activity, answer technical questions truthfully, and de-escalate the inquiry without unnecessarily implicating your coworker or making false statements.",
        stress_points=[
            "The time gap between badge exit and sensor latching.",
            "Inquiries about whether any unauthorized individuals entered.",
            "Strategic pauses after you describe your exit routine.",
        ],
        difficulty="easy",
    ),
    "petty_cash": DualTrackBrief(
        scenario_id="petty_cash",
        title="The Short Drawer",
        role="Office Coordinator & Petty Cash Custodian",
        open_knowledge=[
            "You manage routine supply requests and office incidentals.",
            "The petty cash lockbox key is accessible to designated office staff.",
            "Monthly reconciliation receipts are kept in the administrative binder.",
        ],
        restricted_facts=[
            "You took $40 from the drawer to pay an urgent municipal parking fine, planning to reimburse it before end of week.",
            "You previously told a coworker you hadn't accessed the box that morning.",
            "You feel pressured because an unannounced audit happened before you could deposit the repayment.",
        ],
        objective="Professionally explain drawer access procedures, resist impulse over-explanation during silences, and avoid making unfounded accusations against other keyholders.",
        stress_points=[
            "Direct questions regarding exact morning timeline.",
            "Discrepancies between logged counts and physical cash.",
            "Presumptive assertions suggesting you were seen opening the drawer.",
        ],
        difficulty="medium",
    ),
    "resume_gap": DualTrackBrief(
        scenario_id="resume_gap",
        title="The Suspicious Gap",
        role="Senior Technology Contractor",
        open_knowledge=[
            "You have twelve years of enterprise software architecture experience.",
            "You successfully passed all background security clearances for the current contract.",
            "You have strong reference letters from three prior enterprise engagements.",
        ],
        restricted_facts=[
            "A two-year gap listed as 'independent technology consulting' followed an abrupt termination from a previous firm due to internal conflict.",
            "You have no corporate tax filings for the consulting entity.",
            "You fear disclosure will lead to contract disqualification.",
        ],
        objective="Confidently substantiate your technical competence, maintain professional poise under presumptive questions, and resolve compliance requests without fabricating verifiable corporate records.",
        stress_points=[
            "Requests for 1099 client records and registered corporate entity names.",
            "Sudden jumps in chronological inquiry.",
            "Vocal baseline changes when discussing prior managers.",
        ],
        difficulty="hard",
    ),
}


def get_dual_track_brief(scenario_id: str = "") -> DualTrackBrief:
    if not scenario_id:
        return DUAL_TRACK_BRIEFS["audit_ledger"]
    if scenario_id in DUAL_TRACK_BRIEFS:
        return DUAL_TRACK_BRIEFS[scenario_id]
    raise KeyError(f"No such dual-track brief: {scenario_id!r}. Known: {list(DUAL_TRACK_BRIEFS.keys())}")


def list_dual_track_briefs(difficulty: str | None = None) -> list[DualTrackBrief]:
    briefs = list(DUAL_TRACK_BRIEFS.values())
    if difficulty is None:
        return briefs
    return [b for b in briefs if b.difficulty == difficulty]

