from app.ingest.table_to_prose import tables_to_prose


FIXTURE = """Some intro prose here.

This is a paragraph before the table.

| Spec  | Value   |
| ----- | ------- |
| Color | Red     |
| Size  | *Large* |

Some text between tables.

| Name    | Age | City |
|---------|-----|------|
| Alice   | 30  | NYC  |
| `Bob`   | 25  | LA   |

Final paragraph of prose.
"""


def test_no_leftover_table_syntax():
    result = tables_to_prose(FIXTURE)
    assert "|" not in result
    assert "---" not in result


def test_two_column_table_becomes_sentences():
    result = tables_to_prose(FIXTURE)
    # 2-column tables are the common key/value spec-sheet shape: headers are
    # dropped and the row's own values become subject and predicate, e.g. a
    # real "Spec | Value" row ("Operating Temp", "-20C to 70C") reads as
    # "The Operating Temp is -20C to 70C." — not "The Spec is Operating Temp".
    assert "The Color is Red." in result
    assert "The Size is Large." in result
    assert "The Spec is" not in result


def test_three_column_table_becomes_sentences():
    result = tables_to_prose(FIXTURE)
    assert "The Name is Alice, the Age is 30, the City is NYC." in result
    assert "The Name is Bob, the Age is 25, the City is LA." in result


def test_surrounding_prose_untouched():
    result = tables_to_prose(FIXTURE)
    assert "Some intro prose here." in result
    assert "This is a paragraph before the table." in result
    assert "Some text between tables." in result
    assert "Final paragraph of prose." in result

    # The blank-line spacing around the untouched paragraphs is preserved
    # verbatim (not just the paragraph text itself).
    assert "Some intro prose here.\n\nThis is a paragraph before the table.\n\n" in result
    assert "\n\nFinal paragraph of prose.\n" in result


def test_two_column_row_with_either_side_empty_is_dropped():
    # A 2-column row needs BOTH its subject and predicate values to say
    # anything meaningful ("The Alpha is" and "The  is Beta" are both
    # meaningless) — such rows are dropped entirely, not partially rendered.
    markdown = (
        "| Key | Value |\n"
        "| --- | --- |\n"
        "| Alpha |  |\n"
        "|  | Beta |\n"
        "| Gamma | Delta |\n"
    )
    result = tables_to_prose(markdown)
    assert "is ." not in result
    assert "is ," not in result
    assert "Alpha" not in result
    assert "Beta" not in result
    assert "The Gamma is Delta." in result


def test_three_column_empty_cells_are_skipped_not_rendered_as_dangling_is():
    # 3+ column tables stay header-qualified, so a single missing value can
    # be skipped while the rest of the row's pairs still render.
    markdown = (
        "| Key | Value | Note |\n"
        "| --- | --- | --- |\n"
        "| Alpha |  | first |\n"
        "|  | Beta | second |\n"
    )
    result = tables_to_prose(markdown)
    assert "is ." not in result
    assert "is ," not in result
    assert "The Key is Alpha, the Note is first." in result
    assert "The Value is Beta, the Note is second." in result


def test_emphasis_characters_stripped_from_cells():
    markdown = (
        "| Spec | Value |\n"
        "| --- | --- |\n"
        "| **Bold** | `code` |\n"
        "| _Italic_ | plain |\n"
    )
    result = tables_to_prose(markdown)
    assert "*" not in result
    assert "`" not in result
    assert "_" not in result
    assert "The Bold is code." in result
    assert "The Italic is plain." in result


def test_no_table_leaves_text_completely_unchanged():
    plain = "Just some prose.\n\nNo tables here at all.\n"
    assert tables_to_prose(plain) == plain


def test_row_sentences_are_blank_line_separated_so_large_tables_stay_splittable():
    # Regression test: joining row-sentences with a bare "\n" made an entire
    # table -- however large -- one indivisible paragraph block for
    # chunker.py's oversized-section splitter (confirmed in practice: a real
    # large table produced a single 16,000+ word chunk). Each row is an
    # independent statement, so rows must be blank-line separated to stay
    # independently splittable.
    from app.ingest.chunker import chunk_markdown

    rows = "\n".join(f"| Item{i} | Value{i} |" for i in range(200))
    markdown = f"# Big Table\n\n| Key | Value |\n| --- | --- |\n{rows}\n"
    prose = tables_to_prose(markdown)

    assert "The Item0 is Value0.\n\nThe Item1 is Value1." in prose

    chunks = chunk_markdown(prose, min_tokens=300, max_tokens=600)
    assert len(chunks) > 1, "a 200-row table should split into multiple chunks, not stay as one"
    assert all(len(c["text"].split()) <= 600 * 1.5 for c in chunks)
