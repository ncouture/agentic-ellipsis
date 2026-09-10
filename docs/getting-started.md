# Getting Started with Agentic Ellipsis

This guide walks you through setting up your environment, ingesting behavioral manuals into the hybrid index, launching the agent, and running the test suite.

---

## 1. Prerequisites

- **Python 3.11+**
- **Google GenAI / Gemini API Key:** A valid API key with access to `gemini-3.1-flash-live-preview` (for the live agent) and `text-embedding-004` (for dense retrieval embeddings).

Set your API key in your environment:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
# Alternatively, GOOGLE_API_KEY is also recognized
export GOOGLE_API_KEY="your-gemini-api-key"
```

---

## 2. Environment Setup & Installation

Clone or navigate to the project directory:
```bash
cd /path/to/agentic-ellipsis
```

Create and activate a Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

Core dependencies installed:
- `google-adk`: Agent framework runtime
- `google-genai`: Gemini Live and Embedding API SDK
- `marker-pdf`: PDF to structured markdown parser
- `chromadb`: Vector database for dense semantic embeddings
- `rank-bm25`: BM25 lexical keyword search
- `pytest`: Automated test runner

---

## 3. Ingestion & Index Building

Before running the agent, the source PDF manuals located in [`data/`](../data/) must be processed into chunks and indexed for hybrid retrieval:

```bash
python -m app.scripts.run_ingestion
```

### What Happens During Ingestion:
1. **Extraction:** Marker converts PDFs in `data/` into structured Markdown blocks and tables.
2. **Table-to-Prose:** Markdown tables are converted to descriptive prose chunks to preserve row-column context for embeddings.
3. **Chunking & Validation:** Text is split into semantically coherent blocks with attached metadata (source, category, page range, tags).
4. **Index Generation:** Ingestion outputs artifacts directly into [`index/`](../index/):
   - `index/chunks.jsonl`: Line-delimited raw chunk records.
   - `index/tier1_outline.md`: High-level outline and table of contents for reference.
   - `index/chroma/`: In-process ChromaDB vector store.
   - `index/bm25.pkl` & `index/bm25.ids.json`: Serialized BM25 index and ID mappings.

---

## 4. Running the Agent

Agentic Ellipsis runs on the **Google Agent Development Kit (ADK)** runtime.

### Web Interface
To launch the interactive ADK Web GUI (supporting browser-based voice input and streaming output):
```bash
adk web app
```
Then navigate to the local URL displayed in your console (typically `http://localhost:8000`).

### Terminal / Interactive CLI
To launch directly in your terminal for text-based interaction:
```bash
adk run app
```

---

## 5. Running the Test Suite

Run the full pytest test suite to ensure all unit and integration tests pass:
```bash
pytest
```

Run specific test modules:
```bash
# Test agent tools and mock retrieval
pytest tests/test_agent_tools.py

# Test hybrid search fusion (Chroma + BM25)
pytest tests/test_hybrid.py

# Test latency budgets and warmup verification
pytest tests/test_latency_and_warmup.py
```

---

## 6. Latency Checks & Performance Verification

The system includes pre-configured warmup routines (`app/scripts/warmup.py`) and timing utilities (`app/scripts/latency_check.py`) to verify that index queries stay comfortably under the 50ms latency budget required for live bidirectional voice interaction.

When the agent boots up via `build_root_agent()`, `warm_up()` automatically pre-loads the Chroma collection and BM25 pickle into memory:
```python
from app.scripts.warmup import warm_up
from app.retrieval.gemini_embedding_function import GeminiEmbeddingFunction

warm = warm_up(
    chroma_path="index/chroma",
    collection_name="drill_reference",
    bm25_path="index/bm25.pkl",
    embedding_function=GeminiEmbeddingFunction()
)
```
