# Implementation Plan: Manage Project Dependencies with `uv`

## Phase 1: Project Initialization & Dependency Definition [checkpoint: b96f362]
- [x] Task: Create `pyproject.toml` configuration (e98d900)
    - [x] Define project metadata (`name`, `version`, `requires-python = ">=3.11"`) and `hatchling` build backend
    - [x] Add runtime dependencies (`google-adk`, `marker-pdf`, `chromadb`, `rank-bm25`, `google-genai`)
    - [x] Define `dev` dependency group (`pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`)
- [x] Task: Generate Lockfile and Verify Sync (b96f362)
    - [x] Execute `uv lock` to create deterministic `uv.lock`
    - [x] Execute `uv sync --all-groups` to verify hermetic dependency resolution and editable package installation
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (b96f362)

## Phase 2: Test Suite Verification & Legacy Clean-up [checkpoint: dd9eb22]
- [x] Task: Verify Full Test Suite with `uv run` (f37989d)
    - [x] Run `uv run pytest` across all existing tests (`tests/test_*.py`)
    - [x] Validate test discovery and import resolution under the editable package layout
- [x] Task: Remove Legacy `requirements.txt` (dd9eb22)
    - [x] Delete `requirements.txt`
    - [x] Verify no dangling scripts or tools depend directly on `requirements.txt`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (dd9eb22)

## Phase 3: Documentation & Tech Stack Alignment [checkpoint: e6692fa]
- [x] Task: Update Getting Started Guide (`docs/getting-started.md`) (ddba672)
    - [x] Document `uv` prerequisites and installation
    - [x] Update quickstart steps to use `uv sync` and `uv run`
- [x] Task: Update Tech Stack Context (`conductor/tech-stack.md`) (e6692fa)
    - [x] Document `uv` as the official packaging and dependency management tool
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (e6692fa)

## Phase: Review Fixes
- [x] Task: Apply review suggestions (b0d6498)

