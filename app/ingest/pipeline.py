"""Ingestion pipeline: PDF -> marker (page-tagged blocks) -> table-to-prose ->
header-aware chunks -> per-chunk metadata, plus a per-document outline entry
for the Tier-1 corpus outline.

Known environment limitation: this sandbox has no working OCR vision-fallback
backend for marker/surya (the "vllm" backend needs a working `docker`, which
is broken here; the "llamacpp" backend needs an installed `llama-server`
binary, which isn't present). Ingestion therefore runs with disable_ocr=True.
Digital text, headings, and simple tables extract cleanly this way; a small
number of visually complex, poster/infographic-style "tables" (not simple
rows of data) may extract with garbled or merged cell text as a result.
validate_chunks() (see app.ingest.validate) is meant to surface this rather
than hide it -- it is not silently corrected here.
"""

from __future__ import annotations

import json
import logging
import re

import markdownify

from app.ingest.chunker import chunk_markdown
from app.ingest.metadata import build_chunk_metadata
from app.ingest.table_to_prose import tables_to_prose

logger = logging.getLogger("ingest.pipeline")

_PAGE_ID_RE = re.compile(r"^/page/(\d+)/")
_TAG_RE = re.compile(r"<[^>]+>")


def make_converter():
    """Build one marker PdfConverter, reused across documents to amortize model load time."""
    from marker.config.parser import ConfigParser
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict

    config = {"output_format": "chunks", "disable_ocr": True}
    config_parser = ConfigParser(config)
    return PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
    )


def extract_document_blocks(pdf_path: str, converter) -> list[dict]:
    """Run marker once on a PDF and return its raw "chunks"-format block list.

    Uses model_dump_json() + json.loads() rather than model_dump() -- some
    documents trigger a "TypeError: unhashable type: 'dict'" inside pydantic's
    Python-mode serializer (model_dump()); JSON-mode serialization does not
    hit that path.
    """
    rendered = converter(pdf_path)
    data = json.loads(rendered.model_dump_json())
    return data["blocks"]


def _page_number(block: dict) -> int | None:
    """Extract the true 1-indexed page number from a block's own id.

    The "page" field on a chunks-format block is an internal Page-block ID
    number, NOT a page index -- e.g. a single-page document's blocks all
    report page=801 (that Page block's internal id), not page=0 or page=1.
    The real, sequential page index is embedded in the block's OWN id string
    instead, e.g. "/page/0/SectionHeader/0" -> page index 0 -> page number 1.
    """
    match = _PAGE_ID_RE.match(block.get("id", ""))
    return int(match.group(1)) + 1 if match else None


def _document_markdown_with_page_offsets(blocks: list[dict]) -> tuple[str, list[tuple[int, int]]]:
    """Render a document's blocks into one continuous markdown string, plus a
    list of (start_offset, page_number) breakpoints in that string (one per
    page transition, in order), for recovering page numbers after chunking.

    This chunks the WHOLE document at once, not page by page: chunker.py
    merges small sibling sections forward only when they share a top-level
    ancestor heading, and that ancestor is very often several pages above
    the small section itself (e.g. an H1 that spans 5 pages of H2/H3
    children). Chunking one page in isolation strips that shared ancestor
    from view, so almost every section on a page looks like an orphaned
    top-level section with nothing to merge into -- which is exactly what
    produced a median chunk size of ~9 words on the first ingestion attempt.

    Page recovery is done via character OFFSETS rather than inline text
    markers (e.g. "<!--PAGE:N-->") -- an earlier version tried markers, but
    chunker.py's block-grouping absorbs a trailing marker paragraph into
    whichever heading section is currently open rather than treating it as a
    section boundary, so a marker for page N+1 could end up embedded inside
    page N's own section and mislabel it. Offsets computed here don't depend
    on how chunker.py groups anything.

    tables_to_prose runs PER BLOCK, before concatenation, specifically so its
    text-length changes (a table usually shrinks into shorter prose) never
    shift the offset of any block that comes after it -- each block's start
    offset is exact by construction, not computed by scanning transformed text.
    """
    parts: list[str] = []
    boundaries: list[tuple[int, int]] = []
    offset = 0
    last_page = None

    for block in blocks:
        page_number = _page_number(block)
        html = block.get("html") or ""
        if page_number is None or not html.strip():
            continue

        # heading_style="ATX" is required: markdownify defaults to setext
        # style ("Title\n====") for h1/h2, which chunker.py's heading regex
        # (ATX-only, "#"/"##"/"###") would silently fail to recognize as a
        # heading at all -- collapsing the whole page into one untitled,
        # unheaded blob instead of real sections.
        fragment = markdownify.markdownify(html, heading_style="ATX").strip()
        fragment = tables_to_prose(fragment)
        if not fragment:
            continue

        if page_number != last_page:
            boundaries.append((offset, page_number))
            last_page = page_number

        if parts:
            offset += 2  # the "\n\n" separator this fragment will be joined with
        parts.append(fragment)
        offset += len(fragment)

    return "\n\n".join(parts), boundaries


def document_markdown_from_blocks(blocks: list[dict]) -> str:
    """Render a document's blocks into one continuous, table-to-prose-converted
    markdown string. Thin wrapper over _document_markdown_with_page_offsets
    for callers that only need the text (e.g. debugging/inspection)."""
    text, _ = _document_markdown_with_page_offsets(blocks)
    return text


def _page_for_offset(offset: int, boundaries: list[tuple[int, int]]) -> int:
    """Look up which page a character offset falls under, given the
    (start_offset, page_number) breakpoints from _document_markdown_with_page_offsets."""
    page = boundaries[0][1] if boundaries else 1
    for boundary_offset, boundary_page in boundaries:
        if boundary_offset <= offset:
            page = boundary_page
        else:
            break
    return page


def outline_entry_from_blocks(blocks: list[dict], document_name: str) -> dict:
    """Build a {"document_name", "sections", "key_terms"} entry from a
    document's SectionHeader blocks, for app.ingest.outline.build_tier1_outline.

    key_terms is left empty here rather than having a model invent
    plausible-sounding terms it hasn't verified appear in the source text --
    populate it separately (e.g. from a reviewed glossary) if wanted.
    """
    sections = []
    for block in blocks:
        if block.get("block_type") == "SectionHeader":
            text = _TAG_RE.sub("", block.get("html") or "").strip()
            if text:
                sections.append(text)
    return {"document_name": document_name, "sections": sections, "key_terms": []}


def chunks_from_blocks(blocks: list[dict], document_name: str, summarizer=None) -> list[dict]:
    """Full per-document pipeline from raw marker blocks to indexable chunk dicts.

    Chunks the document's markdown as one continuous stream (see
    _document_markdown_with_page_offsets for why that matters), then
    recovers each resulting chunk's page_number by finding where its own
    text starts within that full document string and looking up which page
    offset-range it falls under. chunk_markdown only ever re-joins
    substrings of its input (grouped/split, never rewritten) using the same
    "\\n\\n" separator the input itself uses, so a chunk's assembled text is
    guaranteed to appear as a contiguous substring of the full document text
    at the point it was extracted from -- this holds regardless of how
    chunker.py internally groups blocks into sections, unlike an inline
    text-marker approach (which broke: a page-transition marker paragraph
    got silently absorbed into whichever heading section was still open,
    mislabeling that section with the NEXT page instead of its own).

    Each returned dict merges chunker.py's output ("text", "section_title",
    "heading_level") with metadata.py's build_chunk_metadata output
    ("document_name", "section_title", "page_number", "summary_one_liner") --
    section_title is present in both and identical, metadata's copy wins the
    merge (same value either way).
    """
    document_markdown, page_boundaries = _document_markdown_with_page_offsets(blocks)
    raw_chunks = chunk_markdown(document_markdown)

    all_chunks: list[dict] = []
    search_cursor = 0
    pages_seen: set[int] = set()

    for chunk in raw_chunks:
        text = chunk["text"]
        start = document_markdown.find(text, search_cursor)
        if start == -1:
            # Should not happen given the substring guarantee above, but
            # don't let a violated assumption silently mislabel the page --
            # fall back to an unanchored search rather than crash.
            start = document_markdown.find(text)
        page_number = _page_for_offset(start, page_boundaries) if start != -1 else 1
        if start != -1:
            search_cursor = start + len(text)
        pages_seen.add(page_number)

        meta = build_chunk_metadata(
            chunk_text=text,
            document_name=document_name,
            section_title=chunk["section_title"],
            page_number=page_number,
            summarizer=summarizer,
        )
        all_chunks.append({**chunk, **meta})

    logger.info(
        "Ingested %s: %d chunk(s) across %d page(s)",
        document_name, len(all_chunks), len(pages_seen),
    )
    return all_chunks
