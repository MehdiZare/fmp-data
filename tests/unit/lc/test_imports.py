# tests/unit/lc/test_imports.py
import importlib

import pytest

from fmp_data.lc import vector_store


def test_langchain_import_paths():
    """Ensure LangChain core import paths are used."""
    pytest.importorskip("langchain_core")

    core_embeddings = importlib.import_module("langchain_core.embeddings").Embeddings
    core_tools = importlib.import_module("langchain_core.tools").StructuredTool

    assert vector_store.Embeddings is core_embeddings
    assert vector_store.StructuredTool is core_tools
