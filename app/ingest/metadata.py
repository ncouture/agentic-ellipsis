"""Build per-chunk metadata for ingested document chunks.

Content-agnostic: this module knows nothing about what the source
documents are about. It only wires together a chunk's structural
metadata (document name, section title, page number) with a short
one-line summary of the chunk text, produced by an injectable
summarizer callable.
"""

from __future__ import annotations

from typing import Callable, Optional

SummarizerFn = Callable[[str], str]

_DEFAULT_MODEL = "gemini-3.5-flash"


def _default_summarizer(text: str) -> str:
    """Real summarizer backed by google-genai.

    Instantiates the client lazily, on first call, so importing this
    module (or calling build_chunk_metadata with an explicit
    summarizer) never requires network access or an API key.
    """
    from google import genai

    client = genai.Client()
    response = client.models.generate_content(
        model=_DEFAULT_MODEL,
        contents=(
            "Summarize this in exactly 10-15 words, plain text, "
            f"no markdown:\n\n{text}"
        ),
    )
    return response.text.strip()


def build_chunk_metadata(
    chunk_text: str,
    document_name: str,
    section_title: str,
    page_number: int,
    summarizer: Optional[SummarizerFn] = None,
) -> dict:
    """Build the metadata dict for a single chunk.

    Args:
        chunk_text: The raw text of the chunk to summarize.
        document_name: Name of the source document.
        section_title: Title of the section the chunk belongs to.
        page_number: Page number the chunk came from.
        summarizer: Optional callable(text: str) -> str used to produce
            the one-line summary. Defaults to a real google-genai backed
            summarizer, constructed lazily (only when this function is
            actually called with summarizer=None).

    Returns:
        A dict with exactly the keys: document_name, section_title,
        page_number, summary_one_liner.
    """
    active_summarizer: SummarizerFn = summarizer if summarizer is not None else _default_summarizer
    summary_one_liner = active_summarizer(chunk_text).strip()

    return {
        "document_name": document_name,
        "section_title": section_title,
        "page_number": page_number,
        "summary_one_liner": summary_one_liner,
    }
