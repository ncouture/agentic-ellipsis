from app.ingest.outline import build_tier1_outline


def _doc(name: str, n_sections: int = 2, n_terms: int = 2) -> dict:
    return {
        "document_name": name,
        "sections": [f"{name} Section {i}" for i in range(1, n_sections + 1)],
        "key_terms": [f"{name.lower()}-term{i}" for i in range(1, n_terms + 1)],
    }


def test_everything_fits_under_max_tokens():
    documents = [
        _doc("Alpha Report"),
        _doc("Beta Manual"),
        _doc("Gamma Notes"),
    ]

    outline = build_tier1_outline(documents, max_tokens=1500)

    for doc in documents:
        assert f"### {doc['document_name']}" in outline
        for section in doc["sections"]:
            assert f"- {section}" in outline
        assert f"Key terms: {', '.join(doc['key_terms'])}" in outline

    assert "dropped" not in outline.lower()


def test_tiny_max_tokens_forces_a_drop():
    documents = [
        _doc("Alpha Report"),
        _doc("Beta Manual"),
        _doc("Gamma Notes"),
    ]

    # Big enough for the first document's block, nowhere near enough for
    # all three.
    first_block_tokens = len(
        "\n".join(
            [
                "### Alpha Report",
                "- Alpha Report Section 1",
                "- Alpha Report Section 2",
                "Key terms: alpha report-term1, alpha report-term2",
            ]
        ).split()
    )

    outline = build_tier1_outline(documents, max_tokens=first_block_tokens)

    assert "### Alpha Report" in outline
    assert "### Beta Manual" not in outline
    assert "### Gamma Notes" not in outline

    lowered = outline.lower()
    assert "dropped" in lowered
    assert "2 document(s) dropped" in outline
    assert "Beta Manual" in outline
    assert "Gamma Notes" in outline


def test_first_document_alone_exceeds_budget_is_dropped_whole():
    documents = [
        _doc("Huge Document", n_sections=20, n_terms=20),
        _doc("Small Doc", n_sections=1, n_terms=1),
    ]

    outline = build_tier1_outline(documents, max_tokens=5)

    # Never truncate mid-document: the oversized doc is dropped entirely,
    # not partially rendered. Truncation is a prefix cut at the document
    # boundary where the budget is first exceeded, so everything from
    # that point on (including the smaller doc that follows it) is
    # reported as dropped -- nothing is silently reordered or skipped.
    assert "### Huge Document" not in outline
    assert "### Small Doc" not in outline
    assert "Huge Document" in outline  # named in the dropped-line
    assert "Small Doc" in outline  # named in the dropped-line
    assert "2 document(s) dropped" in outline


def test_empty_documents_list_returns_empty_string():
    assert build_tier1_outline([], max_tokens=1500) == ""
