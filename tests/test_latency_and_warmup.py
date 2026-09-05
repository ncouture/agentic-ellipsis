"""Tests for app.scripts.latency_check.timed_call and app.scripts.warmup.warm_up."""

from __future__ import annotations

import pickle
import time

import chromadb
import pytest
from rank_bm25 import BM25Okapi

from app.scripts.latency_check import timed_call
from app.scripts.warmup import warm_up


def test_timed_call_fast_within_budget():
    result = timed_call(lambda: 1 + 1, budget_ms=400)

    assert result["result"] == 2
    assert isinstance(result["elapsed_ms"], float)
    assert result["elapsed_ms"] >= 0
    assert result["within_budget"] is True


def test_timed_call_slow_exceeds_budget():
    def slow():
        time.sleep(0.05)
        return "done"

    result = timed_call(slow, budget_ms=1)

    assert result["result"] == "done"
    assert isinstance(result["elapsed_ms"], float)
    assert result["elapsed_ms"] > 1
    assert result["within_budget"] is False


def test_timed_call_never_raises_on_budget_only_reports():
    # A call that blows the budget massively must not raise -- only report.
    result = timed_call(lambda: None, budget_ms=0)
    assert result["within_budget"] is False


def _build_chroma_fixture(chroma_path: str, collection_name: str) -> None:
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.create_collection(name=collection_name)
    collection.add(
        ids=["doc1", "doc2"],
        documents=["the quick brown fox", "jumps over the lazy dog"],
    )


def _build_bm25_fixture(bm25_pickle_path: str) -> None:
    corpus = ["the quick brown fox", "jumps over the lazy dog"]
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    with open(bm25_pickle_path, "wb") as f:
        pickle.dump(bm25, f)


def test_warm_up_loads_both_indexes_with_float_timings(tmp_path):
    chroma_path = str(tmp_path / "chroma")
    collection_name = "test_collection"
    bm25_pickle_path = str(tmp_path / "bm25.pkl")

    _build_chroma_fixture(chroma_path, collection_name)
    _build_bm25_fixture(bm25_pickle_path)

    result = warm_up(
        chroma_path=chroma_path,
        chroma_collection_name=collection_name,
        bm25_pickle_path=bm25_pickle_path,
    )

    assert isinstance(result["chroma_load_ms"], float)
    assert result["chroma_load_ms"] >= 0
    assert isinstance(result["bm25_load_ms"], float)
    assert result["bm25_load_ms"] >= 0

    # Loaded collection object is real and queryable.
    assert result["collection"].count() == 2

    # Loaded BM25 index is real and can score a query.
    scores = result["bm25_index"].get_scores(["quick", "fox"])
    assert len(scores) == 2

    assert isinstance(result["bm25_index"], BM25Okapi)


def test_warm_up_raises_file_not_found_for_missing_chroma_path(tmp_path):
    missing_chroma_path = str(tmp_path / "does_not_exist")
    bm25_pickle_path = str(tmp_path / "bm25.pkl")
    _build_bm25_fixture(bm25_pickle_path)

    with pytest.raises(FileNotFoundError, match="does_not_exist"):
        warm_up(
            chroma_path=missing_chroma_path,
            chroma_collection_name="whatever",
            bm25_pickle_path=bm25_pickle_path,
        )


def test_warm_up_raises_file_not_found_for_missing_bm25_path(tmp_path):
    chroma_path = str(tmp_path / "chroma")
    collection_name = "test_collection"
    _build_chroma_fixture(chroma_path, collection_name)

    missing_bm25_path = str(tmp_path / "missing_bm25.pkl")

    with pytest.raises(FileNotFoundError, match="missing_bm25"):
        warm_up(
            chroma_path=chroma_path,
            chroma_collection_name=collection_name,
            bm25_pickle_path=missing_bm25_path,
        )
