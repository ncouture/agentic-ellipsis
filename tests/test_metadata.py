from app.ingest.metadata import build_chunk_metadata


def fake_summarizer(text: str) -> str:
    return "fake ten to fifteen word summary of the chunk content here"


def test_build_chunk_metadata_returns_exact_keys_and_values():
    result = build_chunk_metadata(
        chunk_text="Some chunk of text extracted from a document.",
        document_name="doc.pdf",
        section_title="Introduction",
        page_number=3,
        summarizer=fake_summarizer,
    )

    assert set(result.keys()) == {
        "document_name",
        "section_title",
        "page_number",
        "summary_one_liner",
    }
    assert result["document_name"] == "doc.pdf"
    assert result["section_title"] == "Introduction"
    assert result["page_number"] == 3
    assert result["summary_one_liner"] == fake_summarizer("irrelevant")


def test_build_chunk_metadata_uses_injected_summarizer_output_for_any_text():
    captured = {}

    def recording_summarizer(text: str) -> str:
        captured["text"] = text
        return "another fake summary that is ten to fifteen words long here"

    result = build_chunk_metadata(
        chunk_text="Chunk body text goes here.",
        document_name="other.md",
        section_title="Conclusion",
        page_number=42,
        summarizer=recording_summarizer,
    )

    assert captured["text"] == "Chunk body text goes here."
    assert result["summary_one_liner"] == "another fake summary that is ten to fifteen words long here"
    assert result["page_number"] == 42


def test_importing_module_does_not_require_api_key(monkeypatch):
    # Importing the module (already done above) must not touch the network
    # or require an API key. Also verify that constructing the default
    # summarizer is deferred: as long as we always pass an explicit
    # summarizer, no google-genai client should ever be instantiated.
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = build_chunk_metadata(
        chunk_text="text",
        document_name="doc.pdf",
        section_title="Section",
        page_number=1,
        summarizer=fake_summarizer,
    )
    assert result["summary_one_liner"] == fake_summarizer("text")
