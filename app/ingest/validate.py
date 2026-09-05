"""Validation checks for ingested chunks.

Content-agnostic: works on any markdown/text corpus. Each chunk is expected
to be a dict produced by combining a chunk's "text" with the metadata dict
built by app/ingest/metadata.py's build_chunk_metadata (which contributes the
keys "document_name", "section_title", "page_number", and
"summary_one_liner").

Two independent checks are run per chunk (by index):
  (a) the chunk's word count falls within a soft bound derived from
      min_tokens/max_tokens, using the same [*0.5, *1.5] slack convention
      used in chunker.py.
  (b) all required metadata keys are present and non-empty/non-None.
"""

from __future__ import annotations

REQUIRED_METADATA_KEYS = (
    "document_name",
    "section_title",
    "page_number",
    "summary_one_liner",
)


def _word_count(text: object) -> int:
    if not isinstance(text, str):
        return 0
    return len(text.split())


def _is_missing(value: object) -> bool:
    """A value counts as missing metadata if it's absent, None, or empty.

    Emptiness is judged the same way for any sized value (strings, lists,
    dicts, etc. via len()); scalars without a length (e.g. an int page
    number) are only considered missing when None.
    """
    if value is None:
        return True
    if hasattr(value, "__len__"):
        try:
            return len(value) == 0
        except TypeError:
            return False
    return False


def validate_chunks(
    chunks: list[dict], min_tokens: int = 300, max_tokens: int = 600
) -> dict:
    """Validate a list of ingested chunks.

    Args:
        chunks: list of chunk dicts, each with a "text" key plus the
            metadata keys produced by build_chunk_metadata.
        min_tokens: lower bound (word-count based) target chunk size.
        max_tokens: upper bound (word-count based) target chunk size.

    Returns:
        {
            "total": len(chunks),
            "out_of_bounds": [indices whose word count fails the soft bound],
            "missing_metadata": [indices missing one or more metadata keys],
            "ok": True iff both lists above are empty,
        }
    """
    low = min_tokens * 0.5
    high = max_tokens * 1.5

    out_of_bounds: list[int] = []
    missing_metadata: list[int] = []

    for i, chunk in enumerate(chunks):
        chunk = chunk or {}

        word_count = _word_count(chunk.get("text"))
        if not (low <= word_count <= high):
            out_of_bounds.append(i)

        if any(_is_missing(chunk.get(key)) for key in REQUIRED_METADATA_KEYS):
            missing_metadata.append(i)

    return {
        "total": len(chunks),
        "out_of_bounds": out_of_bounds,
        "missing_metadata": missing_metadata,
        "ok": not out_of_bounds and not missing_metadata,
    }
