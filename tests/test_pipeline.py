from app.ingest.pipeline import chunks_from_blocks, document_markdown_from_blocks


def _block(page: int, idx: int, block_type: str, html: str) -> dict:
    return {"id": f"/page/{page}/{block_type}/{idx}", "block_type": block_type, "html": html}


def _fake_summarizer(text: str) -> str:
    return "fake summary of chunk content for test purposes only here"


def test_document_markdown_uses_atx_headings_and_contains_body_text():
    blocks = [
        _block(0, 0, "SectionHeader", "<h1>Intro</h1>"),
        _block(0, 1, "Text", "<p>First page text.</p>"),
        _block(1, 0, "Text", "<p>Second page text.</p>"),
    ]
    md = document_markdown_from_blocks(blocks)
    assert "# Intro" in md  # ATX style, not setext ("Intro\n====")
    assert "First page text." in md
    assert "Second page text." in md


def test_document_markdown_converts_table_blocks_to_prose():
    table_html = "<table><thead><tr><th>Spec</th><th>Value</th></tr></thead><tbody><tr><td>Color</td><td>Red</td></tr></tbody></table>"
    blocks = [_block(0, 0, "Table", table_html)]
    md = document_markdown_from_blocks(blocks)
    assert "|" not in md
    assert "The Color is Red." in md


def test_small_sibling_sections_spanning_pages_merge_into_one_chunk():
    # Regression test for the real bug found during ingestion: per-page
    # chunking prevented small H2 sections from merging under their shared
    # H1 parent when that H1 was on an earlier page. Each H2 body here is
    # deliberately tiny (well under min_tokens) so they should merge.
    body = " ".join(f"word{i}" for i in range(20))
    blocks = [
        _block(0, 0, "SectionHeader", "<h1>Parent Topic</h1>"),
        _block(0, 1, "SectionHeader", "<h2>Sub A</h2>"),
        _block(0, 2, "Text", f"<p>{body}</p>"),
        _block(1, 0, "SectionHeader", "<h2>Sub B</h2>"),
        _block(1, 1, "Text", f"<p>{body}</p>"),
        _block(1, 2, "SectionHeader", "<h2>Sub C</h2>"),
        _block(1, 3, "Text", f"<p>{body}</p>"),
    ]
    chunks = chunks_from_blocks(blocks, "doc", summarizer=_fake_summarizer)

    # All three small sibling sections should merge into a single chunk
    # (they share the "Parent Topic" H1 as their top-level ancestor), not be
    # left as three separate ~20-word orphan chunks.
    assert len(chunks) == 1
    assert "Sub B" in chunks[0]["text"] and "Sub C" in chunks[0]["text"]
    assert "word0" in chunks[0]["text"]
    # Merged chunk started on page 0 -> page_number 1 (1-indexed), even
    # though it also contains content from page 1 (Sub B, Sub C).
    assert chunks[0]["page_number"] == 1


def test_page_number_recovered_per_chunk_when_sections_stay_separate():
    # Two large (non-mergeable) top-level sections, one per page: each
    # becomes its own chunk, tagged with its own starting page.
    long_body = " ".join(f"tok{i}" for i in range(350))
    blocks = [
        _block(0, 0, "SectionHeader", "<h1>Chapter One</h1>"),
        _block(0, 1, "Text", f"<p>{long_body}</p>"),
        _block(1, 0, "SectionHeader", "<h1>Chapter Two</h1>"),
        _block(1, 1, "Text", f"<p>{long_body}</p>"),
    ]
    chunks = chunks_from_blocks(blocks, "doc", summarizer=_fake_summarizer)

    assert len(chunks) == 2
    by_title = {c["section_title"]: c for c in chunks}
    assert by_title["Chapter One"]["page_number"] == 1
    assert by_title["Chapter Two"]["page_number"] == 2


def test_chunk_metadata_fields_present():
    body = " ".join(f"w{i}" for i in range(320))
    blocks = [
        _block(0, 0, "SectionHeader", "<h1>Only Section</h1>"),
        _block(0, 1, "Text", f"<p>{body}</p>"),
    ]
    chunks = chunks_from_blocks(blocks, "my_doc", summarizer=_fake_summarizer)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["document_name"] == "my_doc"
    assert chunk["section_title"] == "Only Section"
    assert chunk["page_number"] == 1
    assert chunk["summary_one_liner"] == _fake_summarizer("")
