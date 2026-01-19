# tests/unit/lc/test_imports.py
from langchain_core.embeddings import Embeddings as CoreEmbeddings
from langchain_core.tools import StructuredTool as CoreStructuredTool

from fmp_data.lc import vector_store


def test_langchain_import_paths():
    """Ensure LangChain core import paths are used."""
    assert vector_store.Embeddings is CoreEmbeddings
    assert vector_store.StructuredTool is CoreStructuredTool
