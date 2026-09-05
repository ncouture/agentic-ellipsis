"""Convert GitHub-flavored-markdown pipe tables into narrative prose.

This is a content-agnostic engineering utility: it does not know or care what
a given table is "about". It only understands the generic GFM pipe-table
syntax (header row, a '---' separator row, then data rows) and rewrites each
data row into a single sentence built purely from that row's own header and
cell values.
"""

from __future__ import annotations

import re

# A single pipe-table "line": at least one '|', not itself a separator row.
# We detect tables by scanning line-by-line rather than one big regex so that
# we can precisely control which contiguous block of lines is consumed and
# leave every other line (including blank lines and surrounding paragraphs)
# completely untouched.
_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$|^:?-+:?$")
_EMPHASIS_CHARS_RE = re.compile(r"[*_`]+")


def _split_row(line: str) -> list[str]:
    """Split a pipe-table row into its raw cell strings.

    Handles an optional leading/trailing pipe. Does not attempt to handle
    escaped pipes (\\|) inside cells, which is outside the scope of the
    common GFM tables this function targets.
    """
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(_SEPARATOR_CELL_RE.match(cell.strip()) for cell in cells if cell.strip() != "") and any(
        cell.strip() != "" for cell in cells
    )


def _looks_like_table_row(line: str) -> bool:
    """A line that could plausibly be part of a pipe table (contains a pipe)."""
    return "|" in line.strip()


def _clean_cell(cell: str) -> str:
    """Strip markdown emphasis characters (*, _, backticks) from a cell."""
    return _EMPHASIS_CHARS_RE.sub("", cell).strip()


def _row_to_sentence(headers: list[str], cells: list[str]) -> str | None:
    """Build one narrative sentence from a data row, given the header cells.

    Two-column tables are the common "key/value spec sheet" shape (e.g. a
    row "Operating Temp | -20C to 70C" under headers "Spec | Value"), where
    the natural reading drops the header names entirely and uses the row's
    own values as subject and predicate: "The Operating Temp is -20C to
    70C." Tables with 3+ columns have no single natural subject/predicate
    split, so those stay header-qualified: "The {header_1} is {val_1}, the
    {header_2} is {val_2}, ...".

    Skips fully empty cells (either header or value) rather than emitting
    "is ". Returns None if no usable value remains.
    """
    clean_values = [_clean_cell(cells[i] if i < len(cells) else "") for i in range(len(headers))]

    if len(headers) == 2:
        subject, predicate = clean_values[0], clean_values[1]
        if not subject or not predicate:
            return None
        return f"The {subject} is {predicate}."

    parts: list[str] = []
    for header, value in zip(headers, clean_values):
        clean_header = _clean_cell(header)
        if not clean_header or not value:
            continue
        parts.append(f"the {clean_header} is {value}")

    if not parts:
        return None

    sentence = parts[0]
    if sentence.startswith("the "):
        sentence = "The " + sentence[len("the ") :]
    if len(parts) > 1:
        sentence += ", " + ", ".join(parts[1:])
    sentence += "."
    return sentence


def _find_tables(lines: list[str]) -> list[tuple[int, int, str]]:
    """Locate every pipe-table block in `lines`.

    Returns a list of (start_index, end_index_exclusive, replacement_text)
    tuples, one per table found, in order.
    """
    tables: list[tuple[int, int, str]] = []
    i = 0
    n = len(lines)
    while i < n:
        # A table must start with a header row followed immediately by a
        # valid separator row.
        if _looks_like_table_row(lines[i]) and i + 1 < n:
            header_cells = _split_row(lines[i])
            sep_cells = _split_row(lines[i + 1])
            if (
                len(header_cells) >= 2
                and len(sep_cells) == len(header_cells)
                and _is_separator_row(sep_cells)
            ):
                # We have a table. Consume data rows until one no longer
                # looks like a table row (blank line, prose, EOF, ...).
                start = i
                j = i + 2
                sentences: list[str] = []
                while j < n and _looks_like_table_row(lines[j]):
                    data_cells = _split_row(lines[j])
                    sentence = _row_to_sentence(header_cells, data_cells)
                    if sentence is not None:
                        sentences.append(sentence)
                    j += 1
                # "\n\n" (blank-line separated), not "\n": chunker.py treats a
                # run of newline-joined lines with no blank line between them
                # as ONE indivisible paragraph block. Joining a large table's
                # row-sentences with bare "\n" made the whole table -- however
                # many rows -- a single unsplittable chunk regardless of size
                # (confirmed in practice: a large real-world table produced
                # one 16,000+ word chunk). Each row is an independent factual
                # statement, so giving each its own paragraph lets chunker.py
                # split an oversized table into properly-sized chunks like
                # any other long content.
                replacement = "\n\n".join(sentences)
                tables.append((start, j, replacement))
                i = j
                continue
        i += 1
    return tables


def tables_to_prose(markdown_text: str) -> str:
    """Replace every GFM pipe table in `markdown_text` with narrative prose.

    Each data row of a table becomes one sentence of the form:
        "The {header_1} is {value_1}, the {header_2} is {value_2}, ..."
    Markdown emphasis characters (*, _, `) are stripped from cell contents
    before insertion, and fully empty cells are skipped (no dangling "is ").

    All text outside of detected tables (prose, whitespace, blank lines) is
    left byte-for-byte untouched.
    """
    lines = markdown_text.split("\n")
    tables = _find_tables(lines)

    if not tables:
        return markdown_text

    out: list[str] = []
    cursor = 0
    for start, end, replacement in tables:
        out.extend(lines[cursor:start])
        if replacement:
            out.append(replacement)
        cursor = end
    out.extend(lines[cursor:])

    return "\n".join(out)
