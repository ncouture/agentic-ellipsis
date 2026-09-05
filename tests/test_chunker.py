"""Tests for app.ingest.chunker.chunk_markdown.

Uses a synthetic, content-agnostic fixture built from deterministic
placeholder "words" (e.g. "short0 short1 ...") so word counts are exact
and the tests never depend on what any real corpus is about.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest.chunker import chunk_markdown

MIN_TOKENS = 300
MAX_TOKENS = 600


def _lorem(n: int, prefix: str = "w") -> str:
    """n whitespace-separated placeholder words, e.g. 'w0 w1 w2 ...'."""
    return " ".join(f"{prefix}{i}" for i in range(n))


def _build_fixture() -> str:
    parts = []

    # Content before the first heading -> heading_level 0 chunk.
    parts.append(_lorem(160, "pre"))

    # H1 #1: a small intro body, a deliberately SHORT H2 subsection, a
    # bulleted-list H2 subsection, and a normal-sized H2 subsection.
    # None of these alone reach min_tokens, so they should all merge into
    # one chunk under "Chapter One".
    parts.append("# Chapter One\n\n" + _lorem(40, "c1"))
    parts.append("## Short Subsection\n\n" + _lorem(20, "short"))

    list_block = "\n".join(
        f"- feature item {i} with a bit of descriptive detail padding" for i in range(6)
    )
    parts.append("## Feature List\n\n" + list_block)
    parts.append("## Wrap Up\n\n" + _lorem(220, "wrap"))

    # H1 #2: deliberately LONG (5 paragraphs of 280 words each, well over
    # max_tokens combined) -> should be split at paragraph boundaries.
    long_paragraphs = "\n\n".join(_lorem(280, f"p{k}_") for k in range(5))
    parts.append("# Chapter Two\n\n" + long_paragraphs)

    return "\n\n".join(parts) + "\n"


FIXTURE_MD = _build_fixture()


def test_no_empty_chunks():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    assert len(chunks) > 0
    for c in chunks:
        assert c["text"].strip() != ""


def test_section_title_populated_when_heading_precedes():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    for c in chunks:
        if c["heading_level"] > 0:
            assert c["section_title"], f"chunk with heading_level {c['heading_level']} has no title"
        else:
            # Content preceding the first heading has no heading to report.
            assert c["heading_level"] == 0


def test_word_counts_broadly_within_soft_bounds():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    lo = MIN_TOKENS * 0.5
    hi = MAX_TOKENS * 1.5
    for c in chunks:
        wc = len(c["text"].split())
        assert lo <= wc <= hi, f"chunk word count {wc} outside soft bound [{lo}, {hi}]: {c['text'][:80]!r}"


def test_short_section_gets_merged_into_a_larger_chunk():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    matches = [c for c in chunks if "short0" in c["text"].split()]
    assert len(matches) == 1
    merged_chunk = matches[0]
    # The short subsection (20 words) should have picked up neighboring
    # content rather than standing alone.
    wc = len(merged_chunk["text"].split())
    assert wc > 100
    # It merged with siblings under the same top-level Chapter One heading.
    assert "wrap0" in merged_chunk["text"].split()
    assert merged_chunk["section_title"] == "Chapter One"


def test_long_section_gets_split_into_multiple_chunks():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    chapter_two_chunks = [c for c in chunks if c["section_title"] == "Chapter Two"]
    assert len(chapter_two_chunks) > 1
    for c in chapter_two_chunks:
        wc = len(c["text"].split())
        assert wc <= MAX_TOKENS
        assert c["heading_level"] == 1


def test_bulleted_list_is_never_split_across_chunks():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    list_lines = [f"- feature item {i} with a bit of descriptive detail padding" for i in range(6)]
    containing = [c for c in chunks if list_lines[0] in c["text"]]
    assert len(containing) == 1
    chunk_text = containing[0]["text"]
    for line in list_lines:
        assert line in chunk_text


def test_preamble_before_first_heading_has_heading_level_zero():
    chunks = chunk_markdown(FIXTURE_MD, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    preamble_chunks = [c for c in chunks if "pre0" in c["text"].split()]
    assert len(preamble_chunks) == 1
    assert preamble_chunks[0]["heading_level"] == 0
    assert preamble_chunks[0]["section_title"] == ""


def test_empty_input_returns_no_chunks():
    assert chunk_markdown("") == []
    assert chunk_markdown("   \n\n  \n") == []


def test_heading_levels_and_titles_preserved_when_sections_are_already_big_enough():
    # Each section here already meets min_tokens on its own, so nothing
    # should merge, letting us check heading_level/section_title mapping
    # (including an H2) directly against the source headings.
    md = (
        "# Alpha\n\n"
        + _lorem(MIN_TOKENS + 5, "a")
        + "\n\n## Beta\n\n"
        + _lorem(MIN_TOKENS + 5, "b")
        + "\n\n# Gamma\n\n"
        + _lorem(MIN_TOKENS + 5, "g")
    )
    chunks = chunk_markdown(md, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    assert len(chunks) == 3
    assert chunks[0]["section_title"] == "Alpha"
    assert chunks[0]["heading_level"] == 1
    assert chunks[1]["section_title"] == "Beta"
    assert chunks[1]["heading_level"] == 2
    assert chunks[2]["section_title"] == "Gamma"
    assert chunks[2]["heading_level"] == 1


def test_oversized_unsplittable_paragraph_is_kept_whole_not_truncated():
    # A single paragraph (no blank lines to split on) longer than
    # max_tokens must be kept whole rather than truncated or split
    # mid-paragraph.
    huge_paragraph = _lorem(900, "x")
    chunks = chunk_markdown(huge_paragraph, min_tokens=MIN_TOKENS, max_tokens=MAX_TOKENS)
    assert len(chunks) == 1
    wc = len(chunks[0]["text"].split())
    assert wc == 900
    assert chunks[0]["heading_level"] == 0
