"""Assembles root_agent for the interrogation & behavioral-profiling drill trainer.

Run with `adk web app` or `adk run app` from the project root (once the index
has been built via `python -m app.scripts.run_ingestion`).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from google.adk import Agent

from app.agent.instruction import build_system_instruction
from app.agent.tools import make_query_knowledge_base_tool, start_sprint
from app.retrieval.gemini_embedding_function import GeminiEmbeddingFunction
from app.scripts.warmup import warm_up

logger = logging.getLogger("agent.main")

ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = ROOT / "index"
CHROMA_PATH = str(INDEX_DIR / "chroma")
BM25_PICKLE_PATH = str(INDEX_DIR / "bm25.pkl")
BM25_IDS_PATH = INDEX_DIR / "bm25.ids.json"
OUTLINE_PATH = INDEX_DIR / "tier1_outline.md"
COLLECTION_NAME = "drill_reference"

# Gemini 3.1 Live model for bidirectional streaming (bidiGenerateContent) with native audio support.
LIVE_MODEL = "gemini-3.1-flash-live-preview"


def _load_outline() -> str:
    if not OUTLINE_PATH.exists():
        logger.warning("%s not found -- using fallback outline", OUTLINE_PATH)
        return "Reference index outline pending ingestion."
    return OUTLINE_PATH.read_text()


def build_root_agent() -> Agent:
    tools = [start_sprint]
    try:
        warm = warm_up(CHROMA_PATH, COLLECTION_NAME, BM25_PICKLE_PATH, embedding_function=GeminiEmbeddingFunction())
        bm25_ids = json.loads(BM25_IDS_PATH.read_text()) if BM25_IDS_PATH.exists() else []
        logger.info(
            "Index warmed up: chroma=%.1fms bm25=%.1fms (%d ids)",
            warm["chroma_load_ms"], warm["bm25_load_ms"], len(bm25_ids),
        )

        query_knowledge_base = make_query_knowledge_base_tool(
            bm25_index=warm["bm25_index"],
            bm25_ids=bm25_ids,
            chroma_collection=warm["collection"],
        )
        tools.append(query_knowledge_base)
    except Exception:
        logger.exception("Could not warm up index or load retrieval tool; proceeding with basic tools")

    instruction = build_system_instruction(_load_outline())

    return Agent(
        name="interrogation_drill_trainer",
        model=LIVE_MODEL,
        instruction=instruction,
        tools=tools,
    )


root_agent = build_root_agent()
