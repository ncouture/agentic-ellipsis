# Implementation Plan: Comprehensive Documentation Suite

## Phase 1: Documentation Hub & Getting Started Guide
- [ ] Task: Create `docs/index.md` (Documentation Hub)
    - [ ] Add executive overview and system purpose
    - [ ] Map documentation structure and links to all guides
    - [ ] Document core models and foundational data sources (BTOE, DRS, Authority manuals)
- [ ] Task: Create `docs/getting-started.md` (Developer & Operator Guide)
    - [ ] Document environment setup (Python 3.11+, virtualenv, API keys)
    - [ ] Document data ingestion execution (`app.scripts.run_ingestion`)
    - [ ] Document running the ADK agent (`adk run app`, `adk web app`)
    - [ ] Document latency benchmark checks and test execution (`pytest`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Architecture & Ingestion Pipeline Documentation
- [ ] Task: Create `docs/architecture.md` (System Architecture & Design)
    - [ ] Document Google ADK orchestration and live streaming architecture
    - [ ] Document ChromaDB dense vector & Rank-BM25 sparse lexical hybrid retrieval
    - [ ] Add Mermaid component diagram of system topology
    - [ ] Add Mermaid sequence diagram of turn lifecycle and hybrid query execution
    - [ ] Document warmup caching strategy (`app.scripts.warmup`)
- [ ] Task: Create `docs/pipeline.md` (Ingestion & Knowledge Pipeline)
    - [ ] Document Marker-PDF parser integration and conversion pipeline
    - [ ] Document table-to-prose transform, markdown chunking, and metadata enrichment
    - [ ] Document index build steps and generated artifacts
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Drills, Behavioral Scenarios & Cross-Link Verification
- [ ] Task: Create `docs/drills-and-tools.md` (Agent Tools & Behavioral Drills)
    - [ ] Document all ADK agent tools (`start_sprint`, `reverse_roles`, `teach_interviewing_technique`, `start_whisper_drill`, `query_knowledge_base`)
    - [ ] Document drill scenarios catalog from `app/agent/persona.py` (hidden truths, cover stories, difficulties)
    - [ ] Document BTOE, DRS, and Authority Pillars coaching methodology
- [ ] Task: Cross-Link Verification & Linting
    - [ ] Verify relative links across all files in `docs/`
    - [ ] Validate Mermaid syntax rendering
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
