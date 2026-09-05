"""Build the persistent Chroma + BM25 hybrid index from ingested chunks.

Embedding model note: the architecture spec named "text-embedding-004", which
has been retired -- as of this build the current stable Gemini embedding
model is "gemini-embedding-001" (there's also a newer "gemini-embedding-2",
not yet used here to stay on the non-preview/stable tier). Verified directly
against the account's own model catalog before picking this, rather than
guessing. Swap EMBEDDING_MODEL below if that changes again.
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path

from app.retrieval.hybrid import build_bm25_index

logger = logging.getLogger("retrieval.index_build")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_BATCH_SIZE = 20


def embed_texts(texts: list[str], client=None, model: str = EMBEDDING_MODEL, batch_size: int = EMBEDDING_BATCH_SIZE) -> list[list[float]]:
    """Batch-embed texts via google-genai. Offline/precomputed, not query-time.

    client is injectable for testing without network access.
    """
    from google import genai

    active_client = client if client is not None else genai.Client()
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = active_client.models.embed_content(model=model, contents=batch)
        embeddings.extend(list(e.values) for e in response.embeddings)
    return embeddings


def build_index(
    chunks: list[dict],
    chroma_path: str,
    collection_name: str,
    bm25_pickle_path: str,
    embedding_function=None,
) -> dict:
    """Build and persist the Chroma collection + BM25 index from ingested chunks.

    Args:
        chunks: dicts as produced by app.ingest.pipeline.chunks_from_blocks
            (must have "text", "document_name", "section_title",
            "page_number", "summary_one_liner").
        chroma_path: directory for the chromadb PersistentClient.
        collection_name: name of the collection to (re)create.
        bm25_pickle_path: where to pickle.dump the built BM25Okapi index.
            A sibling "<stem>.ids.json" file is also written with the chunk
            id list in BM25-index order, so a caller can map BM25 result
            positions back to chunk/Chroma ids at query time.
        embedding_function: chromadb EmbeddingFunction to create the
            collection with (Chroma calls it once, batched, over all
            documents passed to add() -- this IS the "batched offline
            pre-computation" step). Defaults to GeminiEmbeddingFunction().
            Must be the SAME embedding function (by .name()) used later when
            re-opening the collection to query it (see app.scripts.warmup),
            or Chroma falls back to a different embedding space at query
            time with no obvious error.

    Returns:
        {"num_chunks", "chroma_path", "collection_name", "bm25_pickle_path", "bm25_ids_path"}
    """
    import chromadb

    if embedding_function is None:
        from app.retrieval.gemini_embedding_function import GeminiEmbeddingFunction

        embedding_function = GeminiEmbeddingFunction()

    ids = [f"chunk-{i}" for i in range(len(chunks))]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {
            "document_name": c["document_name"],
            "section_title": c["section_title"],
            "page_number": c["page_number"],
            "summary_one_liner": c["summary_one_liner"],
        }
        for c in chunks
    ]

    logger.info("Embedding %d chunk(s) via %s...", len(chunks), EMBEDDING_MODEL)

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass  # fine if it didn't exist yet
    collection = client.create_collection(collection_name, embedding_function=embedding_function)
    collection.add(ids=ids, documents=texts, metadatas=metadatas)

    bm25_index = build_bm25_index(texts)
    bm25_path = Path(bm25_pickle_path)
    bm25_path.parent.mkdir(parents=True, exist_ok=True)
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25_index, f)

    ids_path = bm25_path.with_suffix(".ids.json")
    with open(ids_path, "w") as f:
        json.dump(ids, f)

    logger.info(
        "Index built: %d chunk(s) in Chroma collection %r, BM25 index at %s",
        len(chunks), collection_name, bm25_pickle_path,
    )
    return {
        "num_chunks": len(chunks),
        "chroma_path": chroma_path,
        "collection_name": collection_name,
        "bm25_pickle_path": str(bm25_path),
        "bm25_ids_path": str(ids_path),
    }
