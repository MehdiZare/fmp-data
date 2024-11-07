# tests/test_base.py
from unittest.mock import Mock, patch

from fmp_data.base import BaseClient


@patch("httpx.Client.request")
def test_base_client_request(mock_request, mock_endpoint, client_config, mock_response):
    """Test base client request method"""
    mock_request.return_value = mock_response(
        status_code=200, json_data={"test": "data"}
    )

    client = BaseClient(client_config)
    client.request(mock_endpoint)

    # Verify the request was made with correct parameters
    mock_request.assert_called_once()
    mock_endpoint.validate_params.assert_called_once()
    mock_endpoint.build_url.assert_called_once()


@patch("httpx.Client")
def test_base_client_initialization(mock_client_class, client_config):
    """Test base client initialization"""
    mock_client = Mock()
    mock_client_class.return_value = mock_client

    client = BaseClient(client_config)
    assert client.config == client_config
    assert client.logger is not None
    mock_client_class.assert_called_once()


def test_base_client_query_params(client_config):
    """Test query parameter handling"""
    client = BaseClient(client_config)
    test_params = {"param1": "value1"}
    params = client.get_query_params(test_params)
    assert params["apikey"] == client_config.api_key
    assert params["param1"] == "value1"
