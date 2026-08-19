# tests/unit/lc/test_embedding.py - Fixed embedding test
from unittest.mock import patch

import pytest

from fmp_data.exceptions import ConfigError
from fmp_data.lc.embedding import EmbeddingConfig, EmbeddingProvider


@pytest.fixture
def mock_openai():
    with patch("langchain_openai.OpenAIEmbeddings") as mock:
        yield mock


@pytest.fixture
def mock_huggingface():
    with patch("langchain_community.embeddings.HuggingFaceEmbeddings") as mock:
        yield mock


@pytest.fixture
def mock_cohere():
    with patch("langchain_community.embeddings.CohereEmbeddings") as mock:
        yield mock


def test_embedding_config_repr_redacts_secret_kwargs():
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        api_key="test-key",
        additional_kwargs={
            "openai_api_key": "test-provider-key",  # pragma: allowlist secret
            "timeout": 30,
        },
    )
    text = repr(config)
    assert "test-key" not in text
    assert "test-provider-key" not in text
    assert "timeout" in text
    assert "30" in text
    config_with_author = EmbeddingConfig(
        additional_kwargs={"author": "visible", "http_auth": "hidden"}
    )
    author_repr = repr(config_with_author)
    assert "visible" in author_repr
    assert "hidden" not in author_repr


def test_embedding_config_repr_redacts_nested_secret_kwargs():
    """Nested kwargs must be walked, not copied by reference (#273).

    ``OpenAIEmbeddings`` really takes ``default_headers`` and
    ``model_kwargs``, and this config splats them straight into the
    provider, so credentials legitimately live one level down. A
    top-level-only scan printed them verbatim.
    """
    config = EmbeddingConfig(
        additional_kwargs={
            "default_headers": {"Authorization": "Bearer nested-bearer"},
            "model_kwargs": {"api_key": "nested-apikey"},  # pragma: allowlist secret
            "deeply": {"a": {"b": {"token": "nested-deep"}}},
            "in_a_list": [{"password": "nested-in-list"}],  # pragma: allowlist secret
            "harmless": {"temperature": 0.2},
        },
    )
    text = repr(config)

    for secret in (
        "nested-bearer",
        "nested-apikey",
        "nested-deep",
        "nested-in-list",
    ):
        assert secret not in text, f"{secret} leaked into repr: {text}"

    # Non-secret nested data must survive so the repr stays useful.
    assert "temperature" in text
    assert "0.2" in text


def test_embedding_config_repr_does_not_mutate_the_original_kwargs():
    """Redaction returns a copy; the live kwargs still reach the provider."""
    kwargs = {"default_headers": {"Authorization": "Bearer keep-me"}}
    config = EmbeddingConfig(additional_kwargs=kwargs)

    repr(config)

    assert config.additional_kwargs["default_headers"]["Authorization"] == (
        "Bearer keep-me"
    )


def test_embedding_config_validation():
    """Test embedding configuration validation"""
    # Test valid OpenAI config
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        api_key="test-key",
        model_name="text-embedding-ada-002",
    )
    assert config.provider == EmbeddingProvider.OPENAI
    assert config.api_key is not None
    assert config.api_key.get_secret_value() == "test-key"

    # Test valid HuggingFace config without API key
    config = EmbeddingConfig(
        provider=EmbeddingProvider.HUGGINGFACE,
        model_name="sentence-transformers/all-mpnet-base-v2",
    )
    assert config.provider == EmbeddingProvider.HUGGINGFACE


def test_get_embeddings_openai(mock_openai):
    """Test getting OpenAI embeddings"""
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        api_key="test-key",
        model_name="text-embedding-ada-002",
    )

    config.get_embeddings()
    mock_openai.assert_called_once_with(
        openai_api_key="test-key", model="text-embedding-ada-002"
    )


def test_get_embeddings_error_handling():
    """Test embedding error handling"""
    config = EmbeddingConfig(
        provider=EmbeddingProvider.OPENAI,
        model_name="text-embedding-ada-002",
        # Missing API key
    )

    with pytest.raises(ConfigError):
        config.get_embeddings()


def test_get_embeddings_huggingface(mock_huggingface):
    """Test getting HuggingFace embeddings"""
    config = EmbeddingConfig(
        provider=EmbeddingProvider.HUGGINGFACE,
        model_name="sentence-transformers/all-mpnet-base-v2",
    )

    with patch("fmp_data.lc.embedding.check_package_dependency"):
        config.get_embeddings()
    mock_huggingface.assert_called_once_with(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )


def test_get_embeddings_cohere(mock_cohere):
    """Test getting Cohere embeddings"""
    config = EmbeddingConfig(
        provider=EmbeddingProvider.COHERE,
        api_key="test-key",
        model_name="embed-english-v2.0",
    )

    with patch("fmp_data.lc.embedding.check_package_dependency"):
        config.get_embeddings()
    mock_cohere.assert_called_once_with(
        cohere_api_key="test-key", model="embed-english-v2.0"
    )


class TestAdditionalKwargsSerialization:
    """`additional_kwargs` must not leak on the dump path either (#252).

    `SecretStr` cannot reach inside a `dict[str, Any]`, and providers take
    credential-bearing nested kwargs -- `OpenAIEmbeddings` accepts
    `default_headers={"Authorization": ...}`. `repr` was fixed in #273; the
    dump was not, so a structured log or JSON error report still emitted it.
    """

    PLANTED = "PLANTEDCREDENTIAL_aaaa"

    def _config(self) -> EmbeddingConfig:
        return EmbeddingConfig(
            api_key="EMBEDKEY_bbbb",  # pragma: allowlist secret
            additional_kwargs={
                "default_headers": {"Authorization": f"Bearer {self.PLANTED}"},
                "model_kwargs": {"api_key": self.PLANTED},
                "timeout": 30,
            },
        )

    def test_model_dump_does_not_leak_nested_credentials(self) -> None:
        assert self.PLANTED not in str(self._config().model_dump())

    def test_model_dump_json_does_not_leak_nested_credentials(self) -> None:
        assert self.PLANTED not in self._config().model_dump_json()

    def test_repr_still_does_not_leak(self) -> None:
        assert self.PLANTED not in repr(self._config())

    def test_the_live_kwargs_are_untouched(self) -> None:
        """`get_embeddings` splats these into the provider; masking them
        there would authenticate as nobody."""
        config = self._config()
        config.model_dump()  # must not mutate
        assert config.additional_kwargs["model_kwargs"]["api_key"] == self.PLANTED

    def test_non_secret_kwargs_survive_the_dump(self) -> None:
        assert self._config().model_dump()["additional_kwargs"]["timeout"] == 30
