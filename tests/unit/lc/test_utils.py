# tests/lc/test_utils.py
from unittest.mock import Mock, patch

import pytest

from fmp_data.exceptions import DependencyError
from fmp_data.lc.utils import (
    check_embedding_requirements,
    check_package_dependency,
    is_langchain_available,
)


def test_langchain_available():
    """Test langchain availability check"""
    with patch("importlib.util.find_spec") as mock_find_spec:
        # Test when available
        def find_spec_available(name):
            if name in {"langchain_core", "langchain_community"}:
                return Mock()
            return None

        mock_find_spec.side_effect = find_spec_available
        assert is_langchain_available() is True

        # Test when not available
        mock_find_spec.side_effect = None
        mock_find_spec.return_value = None
        assert is_langchain_available() is False


def test_check_package_dependency():
    """Test package dependency check"""
    with patch("importlib.util.find_spec") as mock_find_spec:
        # Test existing package
        mock_find_spec.return_value = Mock()
        check_package_dependency("existing_package", "test")

        # Test missing package
        mock_find_spec.return_value = None
        with pytest.raises(DependencyError):
            check_package_dependency("missing_package", "test")


def test_check_embedding_requirements():
    """Test embedding requirements check"""
    with patch("importlib.util.find_spec") as mock_find_spec:
        # Test OpenAI requirements
        mock_find_spec.return_value = Mock()
        check_embedding_requirements("openai")

        # Test missing requirements
        mock_find_spec.return_value = None
        with pytest.raises(DependencyError):
            check_embedding_requirements("openai")
