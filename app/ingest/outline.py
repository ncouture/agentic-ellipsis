"""Tier-1 outline builder.

Produces a compact Markdown outline over a set of ingested documents, meant
to fit inside a small token budget (e.g. a system-prompt "map" of the
corpus). Token counts are approximated the same way as elsewhere in the
ingestion pipeline (chunker.py): a plain whitespace word count via
``len(text.split())``. This is intentionally crude (no real tokenizer) but
keeps the convention consistent across the codebase.
"""

from __future__ import annotations


def _approx_tokens(text: str) -> int:
    """Approximate token count as a whitespace word count.

    Matches the convention used by chunker.py: ``len(text.split())``.
    """
    return len(text.split())


def _format_document_block(document: dict) -> str:
    """Render a single document's outline block.

    Format::

        ### {document_name}
        - {section 1}
        - {section 2}
        Key terms: {term1, term2, ...}
    """
    name = document.get("document_name", "")
    sections = document.get("sections", []) or []
    key_terms = document.get("key_terms", []) or []

    lines = [f"### {name}"]
    for section in sections:
        lines.append(f"- {section}")
    lines.append(f"Key terms: {', '.join(key_terms)}")
    return "\n".join(lines)


def build_tier1_outline(documents: list[dict], max_tokens: int = 1500) -> str:
    """Build a compact Markdown outline over ``documents``.

    Each document dict is expected to look like::

        {"document_name": str, "sections": list[str], "key_terms": list[str]}

    Documents are rendered in the given order, one "### {document_name}"
    block per document (heading, section bullets, key-terms line). Blocks
    are assembled in order and the running token count (approximated as a
    word count, matching chunker.py's convention) is checked against
    ``max_tokens``.

    If including the next document's block would push the running total
    over ``max_tokens``, assembly stops at that document boundary -- the
    document is never split mid-way. That document and every document after
    it (in the original order) are considered "dropped", and a final line
    is appended stating exactly how many documents were dropped and their
    names, so truncation is never silent.

    Returns the assembled Markdown string. If ``documents`` is empty,
    returns an empty string.
    """
    included_blocks: list[str] = []
    dropped_names: list[str] = []
    total_tokens = 0

    for index, document in enumerate(documents):
        block = _format_document_block(document)
        block_tokens = _approx_tokens(block)

        if total_tokens + block_tokens > max_tokens:
            # Truncate here at a document boundary: this document and all
            # remaining ones (in original order) are dropped.
            dropped_names = [
                doc.get("document_name", "") for doc in documents[index:]
            ]
            break

        included_blocks.append(block)
        total_tokens += block_tokens

    parts = list(included_blocks)
    if dropped_names:
        note = (
            f"_Note: {len(dropped_names)} document(s) dropped due to the "
            f"max_tokens limit: {', '.join(dropped_names)}_"
        )
        parts.append(note)

    return "\n\n".join(parts)
