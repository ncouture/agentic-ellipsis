# Implementation Plan: Comprehensive Documentation Suite

## Phase 1: Documentation Hub & Getting Started Guide
- [x] Task: Create `docs/index.md` (Documentation Hub) (64f9777)
    - [x] Add executive overview and system purpose
    - [x] Map documentation structure and links to all guides
    - [x] Document core models and foundational data sources (BTOE, DRS, Authority manuals)
- [x] Task: Create `docs/getting-started.md` (Developer & Operator Guide) (433028a)
    - [x] Document environment setup (Python 3.11+, virtualenv, API keys)
    - [x] Document data ingestion execution (`app.scripts.run_ingestion`)
    - [x] Document running the ADK agent (`adk run app`, `adk web app`)
    - [x] Document latency benchmark checks and test execution (`pytest`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (433028a)

## Phase 2: Architecture & Ingestion Pipeline Documentation
- [x] Task: Create `docs/architecture.md` (System Architecture & Design) (71042a9)
    - [x] Document Google ADK orchestration and live streaming architecture
    - [x] Document ChromaDB dense vector & Rank-BM25 sparse lexical hybrid retrieval
    - [x] Add Mermaid component diagram of system topology
    - [x] Add Mermaid sequence diagram of turn lifecycle and hybrid query execution
    - [x] Document warmup caching strategy (`app.scripts.warmup`)
- [x] Task: Create `docs/pipeline.md` (Ingestion & Knowledge Pipeline) (e1ee6db)
    - [x] Document Marker-PDF parser integration and conversion pipeline
    - [x] Document table-to-prose transform, markdown chunking, and metadata enrichment
    - [x] Document index build steps and generated artifacts
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (b5c1f96)

## Phase 3: Drills, Behavioral Scenarios & Cross-Link Verification
- [x] Task: Create `docs/drills-and-tools.md` (Agent Tools & Behavioral Drills) (035c384)
    - [x] Document all ADK agent tools (`start_sprint`, `reverse_roles`, `teach_interviewing_technique`, `start_whisper_drill`, `query_knowledge_base`)
    - [x] Document drill scenarios catalog from `app/agent/persona.py` (hidden truths, cover stories, difficulties)
    - [x] Document BTOE, DRS, and Authority Pillars coaching methodology
- [x] Task: Cross-Link Verification & Linting
    - [x] Verify relative links across all files in `docs/`
    - [x] Validate Mermaid syntax rendering
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
