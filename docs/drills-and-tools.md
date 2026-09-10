# Drills, Behavioral Scenarios & Agent Tools: Agentic Ellipsis

This document covers the interactive drill engine, simulation scenarios, behavioral profiling techniques, and the tool interfaces available to the agent runtime in [`app/agent/tools.py`](../app/agent/tools.py).

---

## 1. Drill Architecture & Modes

Agentic Ellipsis supports four complementary training modalities:

| Mode | Tool Trigger | Description | Role of Agent | Role of Trainee |
| :--- | :--- | :--- | :--- | :--- |
| **Standard Sprint** | `start_sprint` | Trainee interviews a simulated subject to elicit a hidden truth. | Simulated Subject | Interviewer / Investigator |
| **Reverse Role** | `reverse_roles` | Trainee defends a cover story while the agent demonstrates elicitation tactics. | Expert Interviewer | Subject / Interviewee |
| **Whisper Drill** | `start_whisper_drill` | Trainee conducts an interview while receiving real-time tactical whispers. | Subject & Discreet Coach | Interviewer |
| **Technique Tutoring** | `teach_interviewing_technique` | Interactive modular lessons on specific interview methodologies. | Field Instructor | Student / Analyst |

---

## 2. ADK Agent Tools Reference

All tools are registered with `google.adk.Agent` and provide structured JSON return payloads.

### `start_sprint(scenario_id: str = "", difficulty: str = "") -> dict`
Initiates a timed interrogation sprint.
- **Parameters:**
  - `scenario_id`: Optional specific scenario ID (e.g., `"badge_favor"`, `"petty_cash"`). If omitted, picks an unvisited scenario.
  - `difficulty`: Optional difficulty filter (`"easy"`, `"medium"`, `"hard"`).
- **Behavior:**
  - Emits the public briefing and initial setup instructions to the trainee.
  - Loads the subject's private hidden truth, personality traits, and cover story into hidden turn state.
  - Switches agent persona into character mode.

### `reverse_roles(scenario_id: str = "", difficulty: str = "") -> dict`
Flips the dynamic to provide defensive practice and demonstrate questioning technique.
- **Parameters:**
  - `scenario_id`: Optional scenario ID.
  - `difficulty`: Optional difficulty filter.
- **Behavior:**
  - Supplies the trainee with their character's secret cover story and hidden facts.
  - Agent adopts the persona of a seasoned investigator using non-accusatory funnel questioning and baseline observation.

### `start_whisper_drill(scenario_id: str = "", whisper_focus: str = "general") -> dict`
Provides real-time feedback during an active questioning session.
- **Parameters:**
  - `scenario_id`: Scenario to run.
  - `whisper_focus`: Specific coaching emphasis (e.g., `"baseline"`, `"timing"`, `"btoe_cues"`, `"rapport"`).
- **Behavior:**
  - Agent replies to questions as the subject, while appending a concise `[WHISPER: ...]` cue (1-2 sentences) pointing out nonverbal shifts or recommended follow-up questions.

### `teach_interviewing_technique(technique_name: str, step: int = 1) -> dict`
Guides the operator through structured, multi-step interviewing lessons.
- **Parameters:**
  - `technique_name`: Name or alias of the technique (e.g., `"funnel_method"`, `"baseline"`).
  - `step`: Specific lesson step (1-indexed).
- **Return Data:**
  - Objective, tactical guidance, example dialogue, behavioral cues to watch, and common pitfalls.

### `query_knowledge_base(query: str, top_k: int = 3) -> dict`
Executes sub-50ms hybrid retrieval over indexed reference manuals.
- **Parameters:**
  - `query`: Free-text search string or behavioral element code (e.g., `"N-14"`, `"collar pull stress indicator"`).
  - `top_k`: Number of fused winning passages to return.
- **Return Data:**
  - List of ranked text passages, source PDF filenames, page numbers, and similarity metadata.

---

## 3. Scenario Catalog (`app/agent/persona.py`)

All drill scenarios are strictly fictional, low-stakes situations designed to isolate specific elicitation challenges without dealing with violent crimes or trauma:

### 1. The Propped Door (`badge_favor`)
- **Difficulty:** Easy
- **Public Briefing:** A restricted server-room door was found propped open after hours. Subject 'Rae' was the last recorded badge swipe.
- **Hidden Truth:** Rae propped the door for a friend from another team who forgot their badge, intending it to be for a minute, but forgot for an hour.
- **Cover Story:** Claims the door latch was faulty and didn't close properly.
- **Primary Skills:** Rapport building, minimization, alleviating fear of third-party consequences.

### 2. The Short Drawer (`petty_cash`)
- **Difficulty:** Medium
- **Public Briefing:** Petty cash drawer is short $40. Subject 'Dana' is one of four keyholders and volunteered to speak first.
- **Hidden Truth:** Dana borrowed $40 to pay an urgent parking citation intending to repay it before inspection, but panicked when questioned.
- **Cover Story:** Insists they haven't touched the drawer in weeks and speculates a courier took it.
- **Primary Skills:** Baseline establishment, timing analysis, identifying overcompensation.

### 3. The Unaccounted Year (`resume_gap`)
- **Difficulty:** Hard
- **Public Briefing:** Discrepancy uncovered in candidate 'Sam's employment history regarding an unlisted 14-month gap between positions.
- **Hidden Truth:** Left former employer during an unpublicized internal audit involving compliance disputes; NDA prohibits discussing details, creating anxiety.
- **Cover Story:** Claims to have taken a sabbatical to travel and care for family.
- **Primary Skills:** Funnel questioning, distinguishing between legal confidentiality and personal deception, detecting cognitive load.

---

## 4. Behavioral Profiling & Technique Methodology

### The Funnel Questioning Method (`funnel_method`)
Moves systematically from broad exploratory questions down to specific clarifiers and inconsistency resolution:
1. **Broad Open-Ended Inquiry:** Establish narrative timeline and baseline fluency without interruptions.
2. **Specific Clarification & Expansion:** Neutral exploration of chronological gaps or anomalies.
3. **Pivotal Direct Clarifiers:** Targeted questions testing whether stated facts align with verifiable physical constraints.

### BTOE (Behavior Table of Elements) Cue Tracking
Trainees learn to observe and catalog nonverbal and verbal behaviors across key categories:
- **Pacifying Behaviors (Neck & Face):** Hand-to-neck contact, collar pulls, suprasternal notch touching.
- **Eye & Gaze Cues:** Blink rate accelerations, pupil changes, auditory/visual recall vectors.
- **Verbal Leakage:** Spontaneous qualifiers ("to be completely honest"), tense shifts, distancing language ("that money").

### Deception Rating Scale (DRS)
A cumulative quantitative framework assigning stress ratings based on temporal clusters of behaviors within 3 to 5 seconds of a stimulus question.

---

## 5. Debriefing & Knowledge Grounding

At the conclusion of each sprint:
1. **Truth Reveal:** The agent reveals the character's `hidden_truth` and compares it against what the trainee successfully elicited.
2. **Behavioral Breakdown:** Highlights key points where the trainee established rapport, applied effective theme development, or missed a pacifying cue.
3. **Methodological Citations:** Uses `query_knowledge_base` to cite specific BTOE elements and Chase Hughes manual passages to reinforce learning.
