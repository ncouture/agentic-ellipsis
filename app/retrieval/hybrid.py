"""Hybrid (BM25 + vector) retrieval over a Chroma collection.

Content-agnostic: nothing here assumes any particular corpus, topic, or
document schema beyond "chunks of text with string IDs".

Integration point picked for `hybrid_search`'s result payloads: the
`chroma_collection` itself is queried a second time via `.get(ids=...)`
after fusion to pull the authoritative `text`/`metadata` for the small
number of fused winners. This was picked over a caller-supplied
id->text/metadata dict because it keeps the function's contract to a
single source of truth (the Chroma collection) and mirrors how a real
caller would use it, while still being trivial to test: build a real
in-memory `chromadb.EphemeralClient()` collection and call straight
into `hybrid_search`.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from rank_bm25 import BM25Okapi

logger = logging.getLogger("hybrid_retrieval")


def _tokenize(text: str) -> list[str]:
    """Whitespace-lowercased tokenization used for BM25 indexing/querying."""
    return text.lower().split()


def build_bm25_index(chunk_texts: list[str]) -> BM25Okapi:
    """Build a BM25Okapi index over whitespace-lowercased tokens of chunk_texts."""
    tokenized_corpus = [_tokenize(text) for text in chunk_texts]
    return BM25Okapi(tokenized_corpus)


def reciprocal_rank_fusion(
    rank_lists: list[list[str]], k: int = 60
) -> list[str]:
    """Standard Reciprocal Rank Fusion over multiple ranked ID lists.

    score(doc) = sum over lists of 1 / (k + rank_in_that_list)

    `rank_in_that_list` is 1-based (the top result in a list contributes
    1 / (k + 1)). A doc absent from a given list contributes 0 for that
    list. Returns doc IDs sorted by fused score descending; ties are
    broken by first-seen order across the input lists for determinism.
    """
    scores: dict[str, float] = {}
    first_seen_order: list[str] = []

    for rank_list in rank_lists:
        for rank0, doc_id in enumerate(rank_list):
            rank = rank0 + 1  # 1-based rank
            if doc_id not in scores:
                scores[doc_id] = 0.0
                first_seen_order.append(doc_id)
            scores[doc_id] += 1.0 / (k + rank)

    order_index = {doc_id: i for i, doc_id in enumerate(first_seen_order)}
    return sorted(
        first_seen_order,
        key=lambda doc_id: (-scores[doc_id], order_index[doc_id]),
    )


def _bm25_ranked_ids(bm25_index: BM25Okapi, bm25_ids: list[str], query: str) -> list[str]:
    """Run a BM25 query and return doc IDs ordered by score descending."""
    scores = bm25_index.get_scores(_tokenize(query))
    ranked = sorted(range(len(bm25_ids)), key=lambda i: scores[i], reverse=True)
    return [bm25_ids[i] for i in ranked]


def _chroma_ranked_ids(chroma_collection: Any, query: str, n_results: int) -> list[str]:
    """Run a Chroma vector query and return doc IDs in Chroma's returned order."""
    result = chroma_collection.query(query_texts=[query], n_results=n_results)
    ids = result.get("ids") or [[]]
    return list(ids[0])


def hybrid_search(
    query: str,
    bm25_index: BM25Okapi,
    bm25_ids: list[str],
    chroma_collection: Any,
    top_k: int = 2,
    latency_budget_ms: int = 250,
) -> list[dict]:
    """Run BM25 and Chroma vector search concurrently, fuse via RRF, return top_k.

    BM25 and the Chroma query are both fast, local/CPU-bound calls, so they
    are run concurrently via a ThreadPoolExecutor rather than asyncio. The
    whole round trip is timed with time.perf_counter; exceeding
    latency_budget_ms logs a WARNING (logger 'hybrid_retrieval') but never
    raises or blocks the caller.
    """
    n_results = max(top_k * 3, 10)
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=2) as executor:
        bm25_future = executor.submit(_bm25_ranked_ids, bm25_index, bm25_ids, query)
        chroma_future = executor.submit(_chroma_ranked_ids, chroma_collection, query, n_results)
        bm25_ranked = bm25_future.result()
        chroma_ranked = chroma_future.result()

    elapsed_ms = (time.perf_counter() - start) * 1000
    if elapsed_ms > latency_budget_ms:
        logger.warning(
            "hybrid_search exceeded latency budget: %.1fms > %dms (query=%r)",
            elapsed_ms,
            latency_budget_ms,
            query,
        )

    fused_ids = reciprocal_rank_fusion([bm25_ranked, chroma_ranked])[:top_k]
    if not fused_ids:
        return []

    fetched = chroma_collection.get(ids=fused_ids)
    fetched_ids = fetched.get("ids") or []
    fetched_documents = fetched.get("documents") or []
    fetched_metadatas = fetched.get("metadatas") or []
    by_id = {
        doc_id: {"text": doc, "metadata": meta}
        for doc_id, doc, meta in zip(fetched_ids, fetched_documents, fetched_metadatas)
    }

    results = []
    for doc_id in fused_ids:
        payload = by_id.get(doc_id, {"text": None, "metadata": None})
        results.append({"id": doc_id, "text": payload["text"], "metadata": payload["metadata"]})
    return results
