"""A chromadb-compatible EmbeddingFunction backed by Gemini's embedding API.

Why this exists rather than just precomputing embeddings and passing plain
query strings to collection.query(query_texts=...): Chroma remembers nothing
about how a collection's vectors were produced unless the collection is both
created AND re-opened with the same EmbeddingFunction. Precomputing at
add() time but querying with bare query_texts= makes Chroma fall back to its
own default local embedder for the query -- silently the wrong embedding
space (dimension mismatch, or worse, a mismatch that doesn't error but just
returns garbage) rather than a visible failure. Wrapping Gemini as a real
EmbeddingFunction and using it consistently at both add() and query() time
avoids that trap entirely, and keeps app.retrieval.hybrid's generic
query_texts=-based hybrid_search working unmodified.
"""

from __future__ import annotations

from chromadb import Documents, EmbeddingFunction, Embeddings

from app.retrieval.index_build import EMBEDDING_MODEL, embed_texts


class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model: str = EMBEDDING_MODEL, client=None):
        self._model = model
        self._client = client

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client()
        return self._client

    def name(self) -> str:
        # Chroma persists this name alongside the collection's config; kept
        # stable across instances so a collection created with one instance
        # of this class validates cleanly against a fresh one after restart.
        return f"gemini-{self._model}"

    def __call__(self, input: Documents) -> Embeddings:
        return embed_texts(list(input), client=self._get_client(), model=self._model)
