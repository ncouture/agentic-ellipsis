# Product Definition: Agentic Ellipsis

## Vision & Overview
Agentic Ellipsis is an interactive, voice-enabled training agent built with Google ADK (Agent Development Kit) and Gemini Live (bidirectional streaming) that trains operators in behavioral profiling, interrogation, and elicitation techniques. Grounded in the Behavior Table of Elements (BTOE) and Chase Hughes' Authority and Ellipsis methodologies, the system provides real-time simulation, live feedback, and indexed knowledge retrieval to build behavioral awareness and interview competence.

## Target Audience & Personas
- **Investigators & Interviewers:** Trainees practicing non-coercive elicitation, deception detection, and baseline analysis.
- **Behavioral Profilers & Operators:** Individuals learning systematic human behavior analysis and gestural/vocal cues (BTOE elements).
- **Communication Specialists:** Operators mastering authority pillars, rapport building, pacing, and verbal influence.

## Core Capabilities & Features
1. **Interactive Drill Scenarios (Sprints):** Simulated role-play exercises with fictional subjects harboring hidden truths and cover stories to practice elicitation.
2. **Reverse Role Drills:** Trainees take on the role of the interviewee or suspect while the AI demonstrates elicitation and profiling techniques.
3. **Live Whisper Coaching:** Real-time hints and observation feeds whispered to the trainee during an interview to guide questioning strategy.
4. **Technique Tutoring:** On-demand instructional sessions explaining core concepts (DRS, BTOE elements, Authority Pillars).
5. **Hybrid Knowledge Retrieval:** Sub-50ms hybrid retrieval combining ChromaDB dense vector search and rank-bm25 lexical search over ingested PDF reference manuals.
6. **Low-Latency Streaming:** Bidirectional streaming via Gemini Live (`gemini-3.1-flash-live-preview`) with native audio support and warm-up caching.

## Success Metrics
- Sub-50ms hybrid retrieval search latency during live agent turns.
- Trainee proficiency improvement in detecting behavioral cues and eliciting admissions.
- Zero factual hallucination on BTOE element codes and official Chase Hughes definitions via strict grounding.
