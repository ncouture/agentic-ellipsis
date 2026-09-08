# Technology Stack: Agentic Ellipsis

## Core Infrastructure
- **Runtime:** Python 3.11+
- **Agent Orchestration:** Google ADK (`google-adk`)
- **LLM / Foundation Model:** Gemini 3.1 Flash Live Preview (`gemini-3.1-flash-live-preview`) via Google GenAI SDK (`google-genai`) for low-latency bidirectional voice/text streaming.

## Retrieval & Ingestion Pipeline
- **Vector Database:** ChromaDB (`chromadb`) using Google Gemini Embeddings (`GeminiEmbeddingFunction`)
- **Lexical Search:** Rank-BM25 (`rank-bm25`) for exact keyword and element code matching
- **Hybrid Fusion:** Combined semantic and lexical retrieval with sub-50ms query latency
- **Document Ingestion:** Marker PDF (`marker-pdf`) extracting text, tables, and structures from behavioral manuals into Markdown & JSON indices.

## Testing & Quality Assurance
- **Test Framework:** Pytest (`pytest`)
- **Test Suites:** Agent tool execution, chunking validation, embedding function integration, hybrid retrieval precision, latency benchmarks, and warmup verification.
