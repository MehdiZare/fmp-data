# tests/unit/lc/conftest.py
import pytest

pytest.importorskip("langchain_core", reason="langchain extra not installed")
pytest.importorskip("langchain_community", reason="langchain extra not installed")
pytest.importorskip("faiss", reason="faiss extra not installed")
