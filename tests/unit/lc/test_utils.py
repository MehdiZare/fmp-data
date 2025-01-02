# tests/lc/test_utils.py
from unittest.mock import Mock, patch

import pytest

from fmp_data.lc.utils import (
    DependencyError,
    check_embedding_requirements,
    check_package_dependency,
    is_langchain_available,
)


def test_langchain_available():
    """Test langchain availability check"""
    with patch("importlib.util.find_spec") as mock_find_spec:
        # Test when available
        mock_find_spec.return_value = Mock()
        assert is_langchain_available() is True

        # Test when not available
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
