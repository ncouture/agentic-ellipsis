# Specification: Manage Project Dependencies with `uv`

## 1. Overview
This track modernizes and standardizes dependency management for Agentic Ellipsis using `uv`. It establishes a modern Python packaging configuration (`pyproject.toml` adhering to PEP 517/518/621) using `hatchling` as the build backend, defines distinct runtime and development dependency groups, generates a deterministic `uv.lock` file, removes legacy `requirements.txt`, and updates project documentation to standardize on `uv run` and `uv sync`.

## 2. Functional Requirements
1. **`pyproject.toml` Definition:**
   - Define project metadata (`name = "adk-ellipsis"`, `version = "0.1.0"`, `requires-python = ">=3.11"`).
   - Configure `hatchling` as build-backend with editable package mapping for `app`.
   - Specify runtime dependencies: `google-adk`, `marker-pdf`, `chromadb`, `rank-bm25`, `google-genai`.
   - Specify development and test dependencies under `[dependency-groups]` / `dev`: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`.
2. **Deterministic Locking & Syncing:**
   - Generate `uv.lock` using `uv lock`.
   - Synchronize virtual environment using `uv sync --all-groups`.
3. **Legacy Clean-up:**
   - Remove `requirements.txt` in favor of declarative `pyproject.toml` and locked `uv.lock`.
4. **Documentation & Tech Stack Updates:**
   - Update `docs/getting-started.md` with instructions for installing `uv`, running `uv sync`, executing tests via `uv run pytest`, and launching the agent via `uv run adk run app`.
   - Update `conductor/tech-stack.md` to document `uv` as the official dependency and environment manager.

## 3. Non-Functional Requirements
- **Reproducibility:** Hermetic, cross-platform deterministic builds guaranteed by `uv.lock`.
- **Performance:** Sub-second dependency resolution and fast cache-driven syncs.
- **Backward Compatibility:** All existing tests (`tests/test_*.py`) must pass unmodified via `uv run pytest`.

## 4. Acceptance Criteria
- [ ] `pyproject.toml` is created and correctly configured with runtime and `dev` dependencies.
- [ ] `uv.lock` is generated and committed to source control.
- [ ] `uv sync` installs the complete environment cleanly.
- [ ] `uv run pytest` runs and passes all test suites.
- [ ] Legacy `requirements.txt` is removed.
- [ ] `docs/getting-started.md` and `conductor/tech-stack.md` are updated to reflect the `uv` workflow.

## 5. Out of Scope
- Publishing `adk-ellipsis` to PyPI or remote registries.
- Upgrading or changing pinned behavior of core model dependencies beyond version compatibility requirements.
