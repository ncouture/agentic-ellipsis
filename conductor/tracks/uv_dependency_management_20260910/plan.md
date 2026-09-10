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

## Phase 2: Test Suite Verification & Legacy Clean-up
- [ ] Task: Verify Full Test Suite with `uv run`
    - [ ] Run `uv run pytest` across all existing tests (`tests/test_*.py`)
    - [ ] Validate test discovery and import resolution under the editable package layout
- [ ] Task: Remove Legacy `requirements.txt`
    - [ ] Delete `requirements.txt`
    - [ ] Verify no dangling scripts or tools depend directly on `requirements.txt`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Documentation & Tech Stack Alignment
- [ ] Task: Update Getting Started Guide (`docs/getting-started.md`)
    - [ ] Document `uv` prerequisites and installation
    - [ ] Update quickstart steps to use `uv sync` and `uv run`
- [ ] Task: Update Tech Stack Context (`conductor/tech-stack.md`)
    - [ ] Document `uv` as the official packaging and dependency management tool
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
