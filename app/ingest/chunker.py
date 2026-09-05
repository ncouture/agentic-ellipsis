"""Markdown chunker for ingestion into the retrieval index.

Splits an arbitrary markdown/text document into retrieval-sized chunks by:

1. Parsing the document into atomic "blocks": headings (H1/H2/H3), list
   blocks (a contiguous run of '-'/'*'/'+'/numbered list-item lines, plus
   any indented continuation lines), and plain paragraphs (a run of
   non-blank, non-list, non-heading lines). Blocks are separated by blank
   lines. A list block is never split internally, even if it uses "loose"
   list formatting with blank lines between items.
2. Grouping blocks into sections at H1/H2/H3 boundaries. Content that
   precedes the first heading forms its own section with heading_level 0.
3. Merging adjacent small sibling sections (sections sharing the same
   immediate parent heading) forward until the accumulated section
   reaches ``min_tokens``. Content before the first heading is never
   merged with anything, since it has no parent heading to share.
4. Splitting any section (merged or not) whose word count exceeds
   ``max_tokens`` back apart at block boundaries (paragraph/list), packing
   blocks greedily so each resulting chunk stays under ``max_tokens``
   where possible. A single block (e.g. one long unsplittable paragraph
   or list) that alone exceeds ``max_tokens`` is kept whole rather than
   truncated or split mid-block.

Token approximation
--------------------
This module has no tokenizer dependency. "Tokens" are approximated as
whitespace-delimited words, i.e. ``len(text.split())``. This is a rough
stand-in for an actual LLM tokenizer (which would typically count
somewhat more sub-word tokens than this counts words), but it is
deterministic, dependency-free, and good enough for sizing chunks within
a soft target range.

This module is intentionally content-agnostic: it does not know or care
what the document is about, and makes no assumptions beyond generic
markdown structure (headings, lists, paragraphs).
"""

from __future__ import annotations

import re

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _word_count(text: str) -> int:
    return len(text.split())


def _parse_blocks(markdown_text: str) -> list[dict]:
    """Split markdown text into an ordered list of atomic blocks.

    Each block is one of:
      {"type": "heading", "level": 1|2|3, "title": str, "raw": str}
      {"type": "list", "raw": str}
      {"type": "para", "raw": str}
    """
    lines = markdown_text.split("\n")
    n = len(lines)
    blocks: list[dict] = []
    i = 0
    while i < n:
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            blocks.append(
                {"type": "heading", "level": level, "title": title, "raw": line.strip()}
            )
            i += 1
            continue

        if _LIST_ITEM_RE.match(line):
            list_lines = [line]
            i += 1
            while i < n:
                cur = lines[i]
                if cur.strip() == "":
                    # Peek past the blank line(s): if a list item or an
                    # indented continuation follows, this is a "loose"
                    # list and the blank line stays inside the block.
                    j = i
                    while j < n and lines[j].strip() == "":
                        j += 1
                    if j < n and not _HEADING_RE.match(lines[j]) and (
                        _LIST_ITEM_RE.match(lines[j]) or lines[j].startswith((" ", "\t"))
                    ):
                        list_lines.append("")
                        i = j
                        continue
                    break
                if _HEADING_RE.match(cur):
                    break
                if _LIST_ITEM_RE.match(cur) or cur.startswith((" ", "\t")):
                    list_lines.append(cur)
                    i += 1
                    continue
                break
            raw = "\n".join(list_lines).strip("\n")
            blocks.append({"type": "list", "raw": raw})
            continue

        # Plain paragraph: consecutive non-blank, non-heading, non-list lines.
        para_lines = [line]
        i += 1
        while i < n:
            cur = lines[i]
            if cur.strip() == "" or _HEADING_RE.match(cur) or _LIST_ITEM_RE.match(cur):
                break
            para_lines.append(cur)
            i += 1
        blocks.append({"type": "para", "raw": "\n".join(para_lines)})

    return blocks


def _render_units(units: list[dict]) -> str:
    return "\n\n".join(u["text"] for u in units if u["text"] and u["text"].strip())


def _build_sections(blocks: list[dict]) -> list[dict]:
    """Group blocks into heading-delimited sections.

    Each section dict has: level, title, group_key (an opaque id shared
    by every section that falls under the same top-level ancestor
    heading -- e.g. an H1's own intro text and all of its H2/H3
    descendants share one group_key -- or None for content with no
    heading), units (the list of renderable {"type", "text"} pieces in
    that section, heading line included), and word_count.
    """
    stack: list[tuple[int, int]] = []  # (level, heading_id)
    roots: dict[int, int] = {}  # heading_id -> id of its top-level ancestor
    heading_counter = 0
    sections: list[dict] = []

    current = {"level": 0, "title": "", "group_key": None, "units": []}

    def _flush(section_state: dict) -> None:
        text = _render_units(section_state["units"])
        if text.strip():
            sections.append(
                {
                    "level": section_state["level"],
                    "title": section_state["title"],
                    "group_key": section_state["group_key"],
                    "units": section_state["units"],
                    "word_count": _word_count(text),
                }
            )

    for block in blocks:
        if block["type"] == "heading":
            _flush(current)
            heading_counter += 1
            hid = heading_counter
            level = block["level"]
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                root = roots[stack[-1][1]]
            else:
                root = hid  # this heading is itself a top-level ancestor
            roots[hid] = root
            stack.append((level, hid))
            current = {
                "level": level,
                "title": block["title"],
                "group_key": root,
                "units": [{"type": "heading", "text": block["raw"]}],
            }
        else:
            current["units"].append({"type": block["type"], "text": block["raw"]})

    _flush(current)
    return sections


def _merge_small_sections(sections: list[dict], min_tokens: int) -> list[dict]:
    """Merge adjacent small sections forward until min_tokens is reached.

    Two sections are eligible to merge if they fall under the same
    top-level ancestor heading (so an H1's own intro merges with its H2
    children, and two small H2/H3 subsections of the same H1 merge with
    each other, but content never merges across a top-level boundary).
    Content with heading_level 0 (no preceding heading) is never merged,
    since it has no heading to share with a neighbor.
    """
    merged: list[dict] = []
    group: dict | None = None

    for sec in sections:
        if sec["level"] == 0:
            if group is not None:
                merged.append(group)
                group = None
            merged.append(
                {
                    "level": 0,
                    "title": "",
                    "units": list(sec["units"]),
                    "word_count": sec["word_count"],
                }
            )
            continue

        if group is None:
            group = {
                "level": sec["level"],
                "title": sec["title"],
                "group_key": sec["group_key"],
                "units": list(sec["units"]),
                "word_count": sec["word_count"],
            }
            continue

        if group["word_count"] < min_tokens and sec["group_key"] == group["group_key"]:
            group["units"].extend(sec["units"])
            group["word_count"] += sec["word_count"]
        else:
            merged.append(group)
            group = {
                "level": sec["level"],
                "title": sec["title"],
                "group_key": sec["group_key"],
                "units": list(sec["units"]),
                "word_count": sec["word_count"],
            }

    if group is not None:
        merged.append(group)

    return merged


def _split_oversized(units: list[dict], max_tokens: int) -> list[list[dict]]:
    """Greedily pack units (in order) into groups under max_tokens.

    Never splits inside a single unit (a paragraph or list block). A unit
    that alone exceeds max_tokens is kept whole in its own group, not
    truncated.
    """
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_count = 0

    for unit in units:
        unit_count = _word_count(unit["text"])
        if current and current_count + unit_count > max_tokens:
            groups.append(current)
            current = []
            current_count = 0
        current.append(unit)
        current_count += unit_count

    if current:
        groups.append(current)

    return groups


def chunk_markdown(markdown_text: str, min_tokens: int = 300, max_tokens: int = 600) -> list[dict]:
    """Chunk a markdown document for retrieval indexing.

    See the module docstring for the full algorithm and the token
    approximation used (word count via ``str.split()``).

    Args:
        markdown_text: the raw markdown/text document to chunk.
        min_tokens: soft lower bound (in approximate tokens/words) a
            chunk should reach before merging stops.
        max_tokens: soft upper bound a chunk should stay under before it
            gets split further; a single unsplittable block larger than
            this is kept whole.

    Returns:
        A list of dicts, each ``{"text": str, "section_title": str,
        "heading_level": int}``. ``heading_level`` is 0 for a chunk built
        from content that precedes the first heading in the document, in
        which case ``section_title`` is "". Never returns empty chunks.
    """
    if not markdown_text or not markdown_text.strip():
        return []

    blocks = _parse_blocks(markdown_text)
    sections = _build_sections(blocks)
    if not sections:
        return []

    merged_groups = _merge_small_sections(sections, min_tokens)

    chunks: list[dict] = []
    for group in merged_groups:
        if group["word_count"] <= max_tokens:
            text = _render_units(group["units"])
            if text.strip():
                chunks.append(
                    {
                        "text": text,
                        "section_title": group["title"],
                        "heading_level": group["level"],
                    }
                )
        else:
            for unit_group in _split_oversized(group["units"], max_tokens):
                text = _render_units(unit_group)
                if text.strip():
                    chunks.append(
                        {
                            "text": text,
                            "section_title": group["title"],
                            "heading_level": group["level"],
                        }
                    )

    return chunks
