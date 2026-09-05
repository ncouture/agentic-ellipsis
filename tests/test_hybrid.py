import logging
import uuid

import chromadb
import pytest

from app.retrieval.hybrid import (
    build_bm25_index,
    hybrid_search,
    reciprocal_rank_fusion,
)

DOCS = {
    "doc-fox": "The quick brown fox jumps over the lazy dog in the park",
    "doc-stocks": "Stock markets rallied today after strong quarterly earnings reports",
    "doc-python": "Python is a popular programming language widely used for data science",
    "doc-cooking": "The chef prepared a delicious pasta dish with fresh tomatoes and basil",
    "doc-ml": "Machine learning models require large amounts of labeled training data",
}

QUERY = "python programming language"
OBVIOUS_MATCH_ID = "doc-python"


def _make_collection():
    client = chromadb.EphemeralClient()
    collection = client.create_collection(name=f"hybrid-test-{uuid.uuid4().hex}")
    ids = list(DOCS.keys())
    texts = list(DOCS.values())
    collection.add(ids=ids, documents=texts, metadatas=[{"source": i} for i in ids])
    return collection, ids, texts


# ---------------------------------------------------------------------------
# reciprocal_rank_fusion
# ---------------------------------------------------------------------------


def test_reciprocal_rank_fusion_matches_hand_computed_scores():
    rank_lists = [
        ["docA", "docB", "docC", "docD"],
        ["docC", "docA", "docE"],
    ]
    k = 60

    # Hand-computed RRF scores (1-based rank):
    # docA = 1/(60+1) + 1/(60+2) = 1/61 + 1/62 ≈ 0.0325225
    # docC = 1/(60+3) + 1/(60+1) = 1/63 + 1/61 ≈ 0.0322665
    # docB = 1/(60+2)            = 1/62        ≈ 0.0161290
    # docE = 1/(60+3)            = 1/63        ≈ 0.0158730
    # docD = 1/(60+4)            = 1/64        ≈ 0.0156250
    # Descending order: docA, docC, docB, docE, docD
    expected_order = ["docA", "docC", "docB", "docE", "docD"]

    assert reciprocal_rank_fusion(rank_lists, k=k) == expected_order


def test_reciprocal_rank_fusion_doc_absent_from_a_list_contributes_zero():
    # "only" appears in just one list; its score is purely from that list.
    rank_lists = [["x", "y"], ["y", "only"]]
    k = 60

    scores = {
        "x": 1.0 / (k + 1),
        "y": 1.0 / (k + 2) + 1.0 / (k + 1),
        "only": 1.0 / (k + 2),
    }
    expected_order = sorted(scores, key=lambda d: -scores[d])

    assert reciprocal_rank_fusion(rank_lists, k=k) == expected_order


def test_reciprocal_rank_fusion_empty_input():
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []


# ---------------------------------------------------------------------------
# build_bm25_index
# ---------------------------------------------------------------------------


def test_build_bm25_index_ranks_keyword_match_highest():
    texts = list(DOCS.values())
    ids = list(DOCS.keys())
    bm25 = build_bm25_index(texts)

    scores = bm25.get_scores(QUERY.lower().split())
    best_idx = max(range(len(ids)), key=lambda i: scores[i])

    assert ids[best_idx] == OBVIOUS_MATCH_ID


# ---------------------------------------------------------------------------
# hybrid_search
# ---------------------------------------------------------------------------


def test_hybrid_search_returns_top_k_and_includes_obvious_match():
    collection, ids, texts = _make_collection()
    bm25_index = build_bm25_index(texts)

    results = hybrid_search(
        query=QUERY,
        bm25_index=bm25_index,
        bm25_ids=ids,
        chroma_collection=collection,
        top_k=2,
    )

    assert len(results) == 2
    result_ids = [r["id"] for r in results]
    assert OBVIOUS_MATCH_ID in result_ids

    # Each result should carry text/metadata pulled from the collection.
    for r in results:
        assert set(r.keys()) == {"id", "text", "metadata"}
        assert r["text"] == DOCS[r["id"]]
        assert r["metadata"] == {"source": r["id"]}


def test_hybrid_search_respects_top_k_of_one():
    collection, ids, texts = _make_collection()
    bm25_index = build_bm25_index(texts)

    results = hybrid_search(
        query=QUERY,
        bm25_index=bm25_index,
        bm25_ids=ids,
        chroma_collection=collection,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == OBVIOUS_MATCH_ID


def test_hybrid_search_warns_but_does_not_raise_when_over_budget(caplog):
    collection, ids, texts = _make_collection()
    bm25_index = build_bm25_index(texts)

    with caplog.at_level(logging.WARNING, logger="hybrid_retrieval"):
        results = hybrid_search(
            query=QUERY,
            bm25_index=bm25_index,
            bm25_ids=ids,
            chroma_collection=collection,
            top_k=2,
            latency_budget_ms=0,  # guarantee the budget is exceeded
        )

    assert len(results) == 2
    assert any(
        record.name == "hybrid_retrieval" and record.levelno == logging.WARNING
        for record in caplog.records
    )
