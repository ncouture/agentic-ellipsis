"""Warm up the retrieval indexes (Chroma + BM25) and time the loads.

Content-agnostic: this module has no idea what corpus the indexes were
built from. It only knows how to open a persisted chromadb collection
and unpickle a persisted rank_bm25.BM25Okapi index, timing each step
separately so callers can see where cold-start latency goes.
"""

from __future__ import annotations

import os
import pickle
import time
from typing import Any


def warm_up(chroma_path: str, chroma_collection_name: str, bm25_pickle_path: str, embedding_function=None) -> dict:
    """Load the Chroma collection and BM25 index, timing each load.

    Args:
        chroma_path: Filesystem path to the chromadb PersistentClient
            directory.
        chroma_collection_name: Name of the collection to load from
            that client.
        bm25_pickle_path: Path to a file previously written with
            pickle.dump of a rank_bm25.BM25Okapi instance.
        embedding_function: optional chromadb EmbeddingFunction to pass to
            get_collection(). Required if the collection was created with a
            custom embedding function (e.g. GeminiEmbeddingFunction) -- Chroma
            does not resurrect an arbitrary custom callable across a process
            restart on its own, so a caller whose collection uses one must
            pass the same one back here (same .name()) or query() will
            silently fall back to a different embedding space. None (the
            default) is correct for a collection using Chroma's own default
            embedding function.

    Returns:
        A dict with exactly the keys:
            chroma_load_ms: float, time to open the client and fetch
                the collection, in milliseconds.
            bm25_load_ms: float, time to unpickle the BM25 index, in
                milliseconds.
            collection: the loaded chromadb collection object.
            bm25_index: the unpickled rank_bm25.BM25Okapi instance.

    Raises:
        FileNotFoundError: if chroma_path or bm25_pickle_path does not
            exist, naming exactly which path is missing and noting
            that the index has not been built yet.
    """
    if not os.path.exists(chroma_path):
        raise FileNotFoundError(
            f"Chroma index not found at {chroma_path!r} -- the index has not "
            "been built yet."
        )
    if not os.path.isfile(bm25_pickle_path):
        raise FileNotFoundError(
            f"BM25 index not found at {bm25_pickle_path!r} -- the index has "
            "not been built yet."
        )

    import chromadb

    start = time.perf_counter()
    client = chromadb.PersistentClient(path=chroma_path)
    if embedding_function is not None:
        collection = client.get_collection(chroma_collection_name, embedding_function=embedding_function)
    else:
        collection = client.get_collection(chroma_collection_name)
    chroma_load_ms = (time.perf_counter() - start) * 1000.0

    # bm25_pickle_path is produced by our own ingest/index-build pipeline
    # (pickle.dump of a rank_bm25.BM25Okapi instance), not user-supplied
    # or externally sourced data, so unpickling it here is trusted.
    start = time.perf_counter()
    with open(bm25_pickle_path, "rb") as f:
        bm25_index: Any = pickle.load(f)
    bm25_load_ms = (time.perf_counter() - start) * 1000.0

    return {
        "chroma_load_ms": chroma_load_ms,
        "bm25_load_ms": bm25_load_ms,
        "collection": collection,
        "bm25_index": bm25_index,
    }
