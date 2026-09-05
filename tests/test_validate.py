from app.ingest.validate import validate_chunks


def _make_text(word_count: int) -> str:
    return " ".join(f"word{i}" for i in range(word_count))


def test_validate_chunks_flags_bad_indices_and_ok_is_false():
    min_tokens, max_tokens = 300, 600

    # 0: fully valid chunk (word count within bounds, all metadata present).
    valid_chunk = {
        "text": _make_text(400),
        "document_name": "policy-handbook.md",
        "section_title": "Introduction",
        "page_number": 3,
        "summary_one_liner": "Overview of the handbook's scope and purpose.",
    }

    # 1: word count far outside the soft bound (too short: below min*0.5).
    too_short_chunk = {
        "text": _make_text(5),
        "document_name": "policy-handbook.md",
        "section_title": "Appendix",
        "page_number": 42,
        "summary_one_liner": "A short appendix note.",
    }

    # 2: valid length, but missing a required metadata field.
    missing_metadata_chunk = {
        "text": _make_text(400),
        "document_name": "policy-handbook.md",
        "section_title": "Definitions",
        "page_number": None,
        "summary_one_liner": "Defines key terms used throughout.",
    }

    chunks = [valid_chunk, too_short_chunk, missing_metadata_chunk]

    result = validate_chunks(chunks, min_tokens=min_tokens, max_tokens=max_tokens)

    assert result["total"] == 3
    assert result["out_of_bounds"] == [1]
    assert result["missing_metadata"] == [2]
    assert result["ok"] is False


def test_validate_chunks_all_valid_is_ok():
    chunk = {
        "text": _make_text(450),
        "document_name": "guide.md",
        "section_title": "Overview",
        "page_number": 1,
        "summary_one_liner": "A one-line summary.",
    }

    result = validate_chunks([chunk], min_tokens=300, max_tokens=600)

    assert result == {
        "total": 1,
        "out_of_bounds": [],
        "missing_metadata": [],
        "ok": True,
    }


def test_validate_chunks_too_long_is_out_of_bounds():
    # max_tokens=600 -> soft upper bound is 900 words.
    chunk = {
        "text": _make_text(1200),
        "document_name": "guide.md",
        "section_title": "Overview",
        "page_number": 1,
        "summary_one_liner": "A one-line summary.",
    }

    result = validate_chunks([chunk], min_tokens=300, max_tokens=600)

    assert result["out_of_bounds"] == [0]
    assert result["missing_metadata"] == []
    assert result["ok"] is False


def test_validate_chunks_empty_string_metadata_counts_as_missing():
    chunk = {
        "text": _make_text(400),
        "document_name": "",
        "section_title": "Overview",
        "page_number": 1,
        "summary_one_liner": "A one-line summary.",
    }

    result = validate_chunks([chunk], min_tokens=300, max_tokens=600)

    assert result["missing_metadata"] == [0]
    assert result["ok"] is False


def test_validate_chunks_empty_list():
    result = validate_chunks([], min_tokens=300, max_tokens=600)

    assert result == {
        "total": 0,
        "out_of_bounds": [],
        "missing_metadata": [],
        "ok": True,
    }
