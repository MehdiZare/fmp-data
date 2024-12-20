from typing import Any

import numpy as np
from langchain.embeddings.base import Embeddings
from langchain.tools.base import StructuredTool
from pydantic import create_model

from fmp_data.models import Endpoint


def create_tool_from_endpoint(endpoint: Endpoint, client: Any) -> StructuredTool:
    """
    Create a StructuredTool from an endpoint definition

    Args:
        endpoint: The endpoint definition
        client: FMP client instance

    Returns:
        A StructuredTool configured for the endpoint
    """

    # Create function to handle endpoint call
    def endpoint_func(**kwargs) -> Any:
        return client.request(endpoint, **kwargs)

    # Get function signature for the tool
    if endpoint.arg_model:
        # Use the arg_model fields for the function parameters
        model_fields = endpoint.arg_model.model_fields
        parameters = {
            name: (field.annotation, ... if field.is_required else None)
            for name, field in model_fields.items()
        }
    else:
        # Create empty parameters if no arg_model
        parameters = {}

    # Create dynamic model for the function parameters
    tool_args_model = create_model(f"{endpoint.name}Args", **parameters)

    return StructuredTool.from_function(
        func=endpoint_func,
        name=endpoint.name,
        description=endpoint.description,
        args_schema=tool_args_model,
    )


def find_relevant_tools(
    query: str,
    endpoints: dict[str, Endpoint],
    embeddings_model: Embeddings,
    client: Any,
    top_n: int = 3,
    similarity_threshold: float = 0.3,
) -> list[StructuredTool]:
    """
    Find relevant endpoints based on query and convert them to tools

    Args:
        query: User's query string
        endpoints: Dictionary of available endpoints
        embeddings_model: Model to use for embeddings
        client: FMP client instance
        top_n: Number of top endpoints to return
        similarity_threshold: Minimum similarity score to include an endpoint

    Returns:
        List of StructuredTools for the most relevant endpoints
    """
    # Create embeddings for query
    query_embedding = embeddings_model.embed_query(query)

    # Calculate similarities for each endpoint
    similarities = []
    for name, endpoint in endpoints.items():
        # Combine description and example queries
        endpoint_text = endpoint.description
        if endpoint.example_queries:
            endpoint_text += " " + " ".join(endpoint.example_queries)

        # Get embedding for endpoint text
        endpoint_embedding = embeddings_model.embed_query(endpoint_text)

        # Calculate cosine similarity
        similarity = np.dot(query_embedding, endpoint_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(endpoint_embedding)
        )

        similarities.append((name, similarity))

    # Sort by similarity and get top N
    top_endpoints = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

    # Convert endpoints to tools if they meet similarity threshold
    tools = []
    for name, similarity in top_endpoints:
        if similarity >= similarity_threshold:
            endpoint = endpoints[name]
            tool = create_tool_from_endpoint(endpoint, client)
            tools.append(tool)

    return tools
