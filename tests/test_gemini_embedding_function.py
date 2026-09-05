from app.retrieval.gemini_embedding_function import GeminiEmbeddingFunction


class _FakeEmbeddings:
    def __init__(self, values):
        self.values = values


class _FakeResponse:
    def __init__(self, vectors):
        self.embeddings = [_FakeEmbeddings(v) for v in vectors]


class _FakeModels:
    def __init__(self):
        self.calls = []

    def embed_content(self, model, contents):
        self.calls.append((model, list(contents)))
        return _FakeResponse([[float(len(text))] * 3 for text in contents])


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()


def test_call_returns_one_vector_per_input_via_injected_client():
    fake_client = _FakeClient()
    ef = GeminiEmbeddingFunction(model="fake-model", client=fake_client)

    result = ef(["ab", "abcd"])

    # chromadb's EmbeddingFunction base wraps __call__'s return value into
    # numpy arrays, so compare via tolist() rather than a direct list == list.
    assert [list(v) for v in result] == [[2.0, 2.0, 2.0], [4.0, 4.0, 4.0]]
    assert fake_client.models.calls == [("fake-model", ["ab", "abcd"])]


def test_name_is_stable_and_derived_from_model():
    ef1 = GeminiEmbeddingFunction(model="model-a")
    ef2 = GeminiEmbeddingFunction(model="model-a")
    ef3 = GeminiEmbeddingFunction(model="model-b")

    assert ef1.name() == ef2.name()
    assert ef1.name() != ef3.name()


def test_client_is_constructed_lazily_not_at_init():
    # No client injected and no API key touched: constructing the object
    # must not require network access or an API key.
    ef = GeminiEmbeddingFunction(model="fake-model")
    assert ef._client is None
