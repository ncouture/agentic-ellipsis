"""End-to-end ingestion runner: data/*.pdf -> index/chunks.jsonl,
index/tier1_outline.md, index/chroma/, index/bm25.pkl.

Usage:
    .venv/bin/python -m app.scripts.run_ingestion
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from app.ingest.outline import build_tier1_outline
from app.ingest.pipeline import chunks_from_blocks, extract_document_blocks, make_converter, outline_entry_from_blocks
from app.ingest.validate import validate_chunks
from app.retrieval.index_build import build_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run_ingestion")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
INDEX_DIR = ROOT / "index"
CHROMA_PATH = str(INDEX_DIR / "chroma")
BM25_PICKLE_PATH = str(INDEX_DIR / "bm25.pkl")
CHUNKS_JSONL_PATH = INDEX_DIR / "chunks.jsonl"
OUTLINE_PATH = INDEX_DIR / "tier1_outline.md"
COLLECTION_NAME = "drill_reference"


def main() -> int:
    pdf_paths = sorted(DATA_DIR.glob("*.pdf"))
    if not pdf_paths:
        logger.error("No PDFs found in %s", DATA_DIR)
        return 1

    converter = make_converter()
    all_chunks: list[dict] = []
    outline_entries: list[dict] = []

    for pdf_path in pdf_paths:
        document_name = pdf_path.stem
        logger.info("Processing %s ...", pdf_path.name)
        blocks = extract_document_blocks(str(pdf_path), converter)
        chunks = chunks_from_blocks(blocks, document_name)
        all_chunks.extend(chunks)
        outline_entries.append(outline_entry_from_blocks(blocks, document_name))

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    with open(CHUNKS_JSONL_PATH, "w") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
    logger.info("Wrote %d chunk(s) to %s", len(all_chunks), CHUNKS_JSONL_PATH)

    report = validate_chunks(all_chunks)
    logger.info("Validation: %s", report)
    if not report["ok"]:
        logger.warning(
            "%d chunk(s) out of soft size bounds, %d missing metadata -- "
            "not blocking the build, but worth a look (see indices above).",
            len(report["out_of_bounds"]), len(report["missing_metadata"]),
        )

    outline = build_tier1_outline(outline_entries)
    OUTLINE_PATH.write_text(outline)
    logger.info("Wrote Tier-1 outline (%d word(s)) to %s", len(outline.split()), OUTLINE_PATH)

    index_info = build_index(all_chunks, CHROMA_PATH, COLLECTION_NAME, BM25_PICKLE_PATH)
    logger.info("Index build complete: %s", index_info)

    return 0


if __name__ == "__main__":
    sys.exit(main())
