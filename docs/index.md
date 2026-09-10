# Agentic Ellipsis Documentation Hub

Welcome to the **Agentic Ellipsis** technical documentation suite. Agentic Ellipsis is an interactive, voice-enabled behavioral profiling and interrogation drill trainer built with the **Google Agent Development Kit (ADK)** and **Gemini Live** (`gemini-3.1-flash-live-preview`).

---

## Executive Overview & System Purpose

Agentic Ellipsis simulates realistic, low-stakes human interactions (such as workplace policy discrepancies and administrative oversights) allowing operators, investigators, and analysts to practice and master behavioral profiling, elicitation techniques, and deception detection.

The agent pairs sub-50ms hybrid retrieval over proprietary behavioral science manuals with conversational roleplay, real-time whisper coaching, and immediate post-drill debriefs.

### Key Tenets
1. **Low-Latency Bidirectional Streaming:** Optimized for real-time voice and text interaction using Gemini Live bidirectional streaming.
2. **Strict Methodological Grounding:** Grounded in Chase Hughes' published works—specifically the Behavior Table of Elements (BTOE), the Deception Rating Scale (DRS), and the Authority Pillars.
3. **Safe, Fictionalized Drill Scenarios:** Scenarios are strictly fictional and low-stakes to allow safe, non-violent, and ethically grounded training.

---

## Foundational Knowledge Sources

The knowledge base indexes source material located in [`data/`](../data/):
- **Behavior Table of Elements (BTOE):** Standardized taxonomy categorizing human nonverbal behaviors, facial movements, and gestural cues with associated stress/deception weightings.
- **Authority Self-Assessment:** Framework covering the six pillars of perceived authority and behavioral dominance.
- **Ellipsis Manual & Training Planner (2017):** Tactical interviewing guidelines, rapport-building frameworks, and elicitation methods.
- **Behavioral Table of Elements ADHD Operator Training Engine:** Interactive matrix mapping cues and interrogation prompts.

---

## Core Models & Technologies

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Agent Orchestration** | [Google ADK](https://github.com/google/adk) | Python agent runtime (`google.adk.Agent`) |
| **Foundation Model** | `gemini-3.1-flash-live-preview` | Low-latency bidirectional audio/text streaming |
| **Vector Store** | ChromaDB (`chromadb`) | In-process dense vector search with cosine similarity |
| **Embeddings** | `GeminiEmbeddingFunction` | Semantic vector representations via Gemini API |
| **Lexical Search** | Rank-BM25 (`rank-bm25`) | In-memory BM25Okapi scoring for exact codes & terminology |
| **Ingestion Engine** | Marker PDF (`marker-pdf`) | High-fidelity PDF to Markdown extraction and table conversion |
| **Test Framework** | Pytest (`pytest`) | Comprehensive unit and latency benchmark suites |

---

## Documentation Navigation

Explore the dedicated documentation guides:

1. [**Getting Started Guide**](./getting-started.md)
   - Environment setup, API keys, dependency installation, running ingestion, starting the agent, and running tests.
2. [**System Architecture & Design**](./architecture.md)
   - High-level component topology, Gemini Live bidirectional turn lifecycle, hybrid search fusion (dense + sparse), and warmup caching.
3. [**Ingestion & Knowledge Pipeline**](./pipeline.md)
   - Marker-PDF parser pipeline, structural table-to-prose transformations, markdown chunking, metadata enrichment, and index building.
4. [**Drills, Scenarios & Agent Tools**](./drills-and-tools.md)
   - Tool execution (`start_sprint`, `reverse_roles`, `teach_interviewing_technique`, `start_whisper_drill`, `query_knowledge_base`), scenario catalog, and coaching methodology.
