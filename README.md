# adk-ellipsis

> **Voice-driven interrogation drill simulator used to train control of high-stakes conversations by relying on subconscious influence, identity alignment, and behavioral profiling.**

---

Built on the **Google Agent Development Kit (ADK)** and **Gemini Live** (`gemini-3.1-flash-live-preview`), **adk-ellipsis** delivers low-latency (<50ms retrieval) spoken audio simulations and drills grounded in Chase Hughes' published behavioral science frameworks:
- **Behavioral Table of Elements (BTOE)**: Standardized taxonomy of gestures, facial micro-expressions, autonomic tells, and deception weights.
- **Deception Rating Scale (DRS)**: Multi-channel cluster analysis and the "Rule of Three" (3+ indicators in a 2-second window).
- **Authority Pillars & The Good Human Test (GHT)**: Identity alignment and non-coercive compliance through competence, likability, authority, and trust.
- **Ellipsis Dialogue & Elicitation Methods**: Subtle truth-elicitation, cognitive load induction, and minimization.

---

## Key Modalities

1. **Standard Sprint** (`start_sprint`):
   - You act as the interviewer/interrogator.
   - The agent roleplays a fictional subject harboring a hidden truth behind a plausible cover story.
   - Features post-drill debriefing grounded in BTOE/DRS theory with concrete scores and citations.

2. **Reverse-Role Sprint** (`reverse_roles`):
   - Roles swap: You play the subject defending a cover story under pressure.
   - The agent acts as the professional interrogator, demonstrating baseline calibration, cognitive load testing, and minimization techniques against you.

3. **Step-by-Step Technique Lessons** (`teach_interviewing_technique`):
   - Structured, sequential masterclasses covering the Funnel Method, Baseline & Norming, Cognitive Load Induction, Minimization & Rationalization, Authority Activation, and Tell Cluster Detection.

4. **Dual-Track Whisper Drills** (`start_whisper_drill`):
   - Operates a primary subject interrogation channel alongside a secondary "tactical earpiece" coach providing live behavioral observations and suggested questions.

---

## Architecture & Technology Stack

- **Agent Runtime**: [Google ADK](https://github.com/google/adk) (`google.adk.Agent`)
- **Foundation Model**: `gemini-3.1-flash-live-preview` (bidirectional audio/text streaming)
- **Hybrid Retrieval Engine**:
  - **Dense Vector**: ChromaDB in-process vector store with Gemini embeddings
  - **Sparse Lexical**: Rank-BM25 (`BM25Okapi`) for exact BTOE element codes and terminology
- **Index Warmup Cache**: Pre-loads indices into memory at boot (<50ms latency)

---

## Quick Start
 
### 1. Installation
```bash
# Synchronize virtual environment with all runtime and development dependencies
uv sync --all-groups
```

### 2. Set API Key
```bash
export GEMINI_API_KEY="your-api-key"
```

### 3. Build Retrieval Index (if starting fresh)
```bash
uv run python -m app.scripts.run_ingestion
```

### 4. Run the Agent
```bash
# Terminal CLI
uv run adk run app

# Web Interface
uv run adk web app
```

### 5. Run Tests
```bash
uv run pytest
```

---

## Using the Project with `uv`

Quick reference commands for common development, testing, and operational workflows using [`uv`](https://docs.astral.sh/uv/):

| Task | Command | Description |
|---|---|---|
| **Environment Sync (Dev)** | `uv sync --all-groups` | Install all runtime and development dependencies in editable mode |
| **Environment Sync (Prod)** | `uv sync` | Install runtime dependencies only without test/dev tools |
| **Run Test Suite** | `uv run pytest` | Execute all unit and integration tests |
| **Test Coverage** | `uv run pytest --cov=app` | Run pytest with module test coverage metrics |
| **Code Quality / Linting** | `uv run ruff check` | Run fast linting across application and tests |
| **Auto-formatting** | `uv run ruff format` | Format code according to project style standards |
| **Run Document Ingestion** | `uv run python -m app.scripts.run_ingestion` | Parse PDFs in `data/` and rebuild `index/` stores |
| **Check Retrieval Latency** | `uv run python -m app.scripts.latency_check` | Verify sub-50ms retrieval benchmark budget |
| **Launch Agent (Terminal)** | `uv run adk run app` | Start interactive CLI session with ADK agent |
| **Launch Agent (Web GUI)** | `uv run adk web app` | Launch ADK Web interface with voice/streaming support |
| **Update Lockfile** | `uv lock` | Regenerate deterministic `uv.lock` |
| **Add Runtime Dependency** | `uv add <package>` | Add and lock a new runtime dependency in `pyproject.toml` |
| **Add Dev Dependency** | `uv add --dev <package>` | Add a development tool to `[dependency-groups]` |

---

## Documentation

Full technical documentation is available in the [`docs/`](docs/) directory:
- [**Documentation Hub**](docs/index.md)
- [**Developer & Operator Getting Started Guide**](docs/getting-started.md)
- [**System Architecture & Design**](docs/architecture.md)
- [**Ingestion & Knowledge Pipeline**](docs/pipeline.md)
- [**Drills, Scenarios & Agent Tools**](docs/drills-and-tools.md)
