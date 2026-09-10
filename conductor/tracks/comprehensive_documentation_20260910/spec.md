# Specification: Comprehensive Documentation Suite

## Overview
Create a complete, high-fidelity documentation suite in `docs/` for Agentic Ellipsis. The documentation will explain the project's system architecture, ingestion pipeline, hybrid retrieval mechanism, agent tools/drills, and developer getting-started guide, complete with Mermaid diagrams and concrete code references.

## Functional Requirements
1. **`docs/index.md` (Documentation Hub):**
   - High-level project summary and navigational guide.
   - Map of core system capabilities, models used (`gemini-3.1-flash-live-preview`), and data sources (BTOE, DRS, Authority manuals).
2. **`docs/architecture.md` (System Design & Architecture):**
   - Architectural overview of Google ADK integration and bidirectional audio/text streaming.
   - ChromaDB dense vector retrieval and Rank-BM25 sparse lexical retrieval architecture.
   - Mermaid diagram: High-level component topology.
   - Mermaid sequence diagram: Live Agent turn lifecycle (audio/text in -> streaming LLM -> tool call `query_knowledge_base` -> hybrid fusion -> low-latency response).
   - Warmup caching strategy (`app.scripts.warmup`).
3. **`docs/pipeline.md` (Ingestion Pipeline):**
   - Marker-PDF parser integration and conversion pipeline.
   - Structural processing: table-to-prose conversion, Markdown chunking, outline extraction (`tier1_outline.md`), and metadata enrichment.
   - Index building process (`app.scripts.run_ingestion`).
4. **`docs/drills-and-tools.md` (Drill Scenarios & Agent Tools):**
   - Breakdown of tools: `start_sprint`, `reverse_roles`, `teach_interviewing_technique`, `start_whisper_drill`, `query_knowledge_base`.
   - Behavioral profiling scenarios in `app/agent/persona.py` (hidden truths, cover stories, difficulty tiers).
   - Interaction modes: Sprints, Reverse Roles, Live Whisper Coaching, Debriefing.
5. **`docs/getting-started.md` (Developer & Operator Guide):**
   - Prerequisites (Python 3.11+, virtualenv, API keys).
   - Ingestion workflow execution.
   - Running the agent with `adk run app` / `adk web app`.
   - Latency benchmark execution (`app.scripts.latency_check`) and test suite verification (`pytest`).

## Non-Functional Requirements
- **Formatting:** Clean GitHub-flavored Markdown with code blocks and cross-links.
- **Accuracy:** Accurate code references matching `app/` and `tests/`.
- **Visuals:** Valid Mermaid syntax for component and sequence diagrams.

## Acceptance Criteria
- All 5 documents are created in `docs/`.
- Cross-references use valid relative links.
- Diagrams render valid Mermaid syntax.

## Out of Scope
- Code modifications to `app/` or `tests/`.
- External static documentation sites (MkDocs, Docusaurus).
