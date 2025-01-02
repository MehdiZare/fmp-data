# fmp_data/lc/manager.py
from logging import Logger

from langchain.tools import StructuredTool

from fmp_data.lc.config import LangChainConfig
from fmp_data.lc.embedding import EmbeddingProvider
from fmp_data.lc.mapping import ENDPOINT_GROUPS
from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.registry import Endpoint, EndpointRegistry
from fmp_data.lc.setup import setup_vector_store
from fmp_data.lc.utils import DependencyError, is_langchain_available
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger


class FMPToolManager:
    """
    Manager for FMP API tools and endpoints with LangChain integration.

    Args:
        fmp_api_key: FMP API key for accessing financial data
        openai_api_key: OpenAI API key for
            embeddings (required if using OpenAI embeddings)
        store_name: Name for the vector store
        auto_initialize: Whether to initialize endpoints and store on creation
        logger: Optional custom logger instance
        endpoint_groups: Dictionary of endpoint groups to load
        config: Optional LangChain configuration
            (if provided, api_keys will override config values)
        embedding_provider: Embedding provider to use (default: OpenAI)
        embedding_model: Optional specific model to use for embeddings

    Examples:
        # Create with both API keys
        manager = FMPToolManager(
            fmp_api_key="your-fmp-key",  # pragma: allowlist secret
            openai_api_key="your-openai-key" # pragma: allowlist secret
        )

        # Create with custom embedding provider
        manager = FMPToolManager(
            fmp_api_key="your-fmp-key",  # pragma: allowlist secret
            embedding_provider=EmbeddingProvider.HUGGINGFACE,
            embedding_model="sentence-transformers/all-mpnet-base-v2"
        )
    """

    def __init__(
        self,
        fmp_api_key: str | None = None,
        openai_api_key: str | None = None,
        store_name: str = "fmp_endpoints",
        auto_initialize: bool = True,
        logger: Logger | None = None,
        endpoint_groups: dict[str, dict] = ENDPOINT_GROUPS,
        config: LangChainConfig | None = None,
        embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI,
        embedding_model: str | None = None,
    ):
        """Initialize tool manager."""
        if not is_langchain_available():
            raise DependencyError(
                "LangChain is required. Install with: "
                "pip install 'fmp-data[langchain]'"
            )

        try:
            # Initialize logger first
            self.logger = logger or FMPLogger().get_logger(__name__)

            # Set up configuration
            self.config = self._setup_config(
                config=config,
                fmp_api_key=fmp_api_key,
                openai_api_key=openai_api_key,
                embedding_provider=embedding_provider,
                embedding_model=embedding_model,
            )

            # Initialize components
            from fmp_data import FMPDataClient

            self.client = FMPDataClient(config=self.config)
            self.registry = EndpointRegistry()
            self.store_name = store_name
            self.endpoint_groups = endpoint_groups
            self._loaded_groups = {group: False for group in endpoint_groups.keys()}
            self.vector_store: EndpointVectorStore | None = None

            if auto_initialize:
                self.initialize()

        except Exception as e:
            self.logger.error(f"Failed to initialize tool manager: {str(e)}")
            raise

    def _setup_config(
        self,
        config: LangChainConfig | None,
        fmp_api_key: str | None,
        openai_api_key: str | None,
        embedding_provider: EmbeddingProvider,
        embedding_model: str | None,
    ) -> LangChainConfig:
        """Set up configuration with API keys and embedding settings."""
        try:
            if config is None:
                # Create new config with required fmp_api_key
                if not fmp_api_key:
                    # Try to get from environment if not provided
                    config = LangChainConfig.from_env()
                else:
                    config = LangChainConfig(api_key=fmp_api_key)

            # Update embedding settings
            config.embedding_provider = embedding_provider
            if embedding_model:
                config.embedding_model = embedding_model

            # Handle OpenAI API key
            if embedding_provider == EmbeddingProvider.OPENAI:
                if openai_api_key:
                    config.embedding_api_key = openai_api_key
                elif not config.embedding_api_key:
                    # Try to get from environment
                    import os

                    env_key = os.getenv("OPENAI_API_KEY")
                    if env_key:
                        config.embedding_api_key = env_key
                    else:
                        self.logger.warning(
                            "No OpenAI API key provided or found in environment"
                        )

            return config

        except Exception as e:
            self.logger.error(f"Failed to setup configuration: {str(e)}")
            raise

    def initialize(self) -> None:
        """Initialize endpoints and vector store"""
        try:
            self.logger.info("Initializing FMP Tool Manager")
            self.load_all_endpoints()

            if not self.registry.list_endpoints():
                raise RuntimeError("No endpoints were registered during initialization")

            # Get embeddings from config
            if not self.config.embedding_config:
                raise RuntimeError(
                    "Embedding configuration required. Set via environment "
                    "variables or provide config with embedding settings."
                )

            embeddings = self.config.embedding_config.get_embeddings()
            self.vector_store = setup_vector_store(
                client=self.client,
                registry=self.registry,
                embeddings=embeddings,
                store_name=self.store_name,
            )

            if not self.vector_store:
                raise RuntimeError("Failed to initialize vector store")

        except Exception:
            self.logger.error("Failed to initialize tool manager", exc_info=True)
            raise

    def initialize_vector_store(self, force_create: bool = False) -> None:
        """
        Initialize or load vector store.

        Args:
            force_create: Whether to force creation of a new store
        """
        if self.vector_store is not None and not force_create:
            self.logger.debug("Vector store already initialized")
            return

        try:
            embeddings = self.config.embedding_config.get_embeddings()
            self.vector_store = setup_vector_store(
                client=self.client,
                registry=self.registry,
                embeddings=embeddings,
                store_name=self.store_name,
                force_create=force_create,
            )
            self.logger.info(
                f"Initialized vector store with "
                f"{len(self.registry.list_endpoints())} endpoints"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize vector store: {str(e)}") from e

    def _register_endpoints(
        self,
        endpoint_map: dict[str, Endpoint],
        semantics_map: dict[str, EndpointSemantics],
    ) -> tuple[int, set[str], set[str]]:
        """Register endpoints with validation."""
        registered = set()
        skipped = set()

        for name, endpoint in endpoint_map.items():
            try:
                semantic_name = name[4:] if name.startswith("get_") else name
                semantics = semantics_map.get(semantic_name)

                if not semantics:
                    self.logger.debug(
                        f"No semantics found for endpoint {name} "
                        f"(semantic_name: {semantic_name})"
                    )
                    skipped.add(name)
                    continue

                self.registry.register(name, endpoint, semantics)
                registered.add(name)

            except Exception as e:
                self.logger.error(f"Failed to register {name}: {str(e)}", exc_info=True)
                skipped.add(name)

        return len(registered), registered, skipped

    def load_endpoints(
        self, endpoint_map: dict, semantics_map: dict, group_name: str
    ) -> tuple[int, set[str], set[str]]:
        """
        Load endpoints for a specific group.

        Args:
            endpoint_map: Dictionary of endpoints
            semantics_map: Dictionary of semantic information
            group_name: Name of the endpoint group

        Returns:
            Tuple of (number registered, registered endpoints, skipped endpoints)
        """
        if not endpoint_map:
            raise ValueError(f"Empty endpoint map provided for group {group_name}")
        if not semantics_map:
            raise ValueError(f"Empty semantics map provided for group {group_name}")

        try:
            return self._register_endpoints(endpoint_map, semantics_map)
        except Exception as e:
            self.logger.error(
                f"Failed to load {group_name} endpoints: {str(e)}", exc_info=True
            )
            raise RuntimeError(
                f"Error loading endpoints for {group_name}: {str(e)}"
            ) from e

    def load_all_endpoints(self) -> None:
        """Load all available endpoint groups"""
        total_registered = 0
        all_registered = set()
        all_skipped = set()
        loaded_groups = []

        try:
            for group_name, config in self.endpoint_groups.items():
                if self._loaded_groups.get(group_name):
                    continue

                count, registered, skipped = self.load_endpoints(
                    config["endpoint_map"], config["semantics_map"], group_name
                )
                self._loaded_groups[group_name] = True
                total_registered += count
                all_registered.update(registered)
                all_skipped.update(skipped)
                loaded_groups.append(config["display_name"])

            # Log registration results
            if all_skipped:
                self.logger.warning(
                    f"Failed to register {len(all_skipped)} "
                    f"endpoints: {sorted(all_skipped)}"
                )

            self.logger.info(
                f"Successfully registered {len(all_registered)} endpoints across "
                f"{len(loaded_groups)} groups: {', '.join(loaded_groups)}"
            )

            # Log detailed statistics
            total_attempted = len(all_registered) + len(all_skipped)
            success_rate = (
                f"{(len(all_registered) / total_attempted * 100):.1f}%"
                if total_attempted > 0
                else "0.0%"
            )

            self.logger.debug(
                "Registration details",
                extra={
                    "registered": len(all_registered),
                    "skipped": len(all_skipped),
                    "total_attempted": total_attempted,
                    "success_rate": success_rate,
                },
            )

        except Exception as e:
            self.logger.error(f"Failed to load endpoints: {str(e)}", exc_info=True)
            raise

    def _get_embeddings(self):
        """Get embeddings from config or raise error"""
        if not self.config.embedding:
            raise RuntimeError(
                "Embedding configuration not found. "
                "Please configure embeddings in client config or environment variables."
            )
        return self.config.embedding.get_embeddings()

    def get_tools(
        self, query: str | None = None, k: int = 3, threshold: float = 0.3
    ) -> list[StructuredTool]:
        """
        Get relevant LangChain tools based on natural language query.

        Args:
            query: Natural language query to find relevant tools (None for all tools)
            k: Maximum number of tools to return
            threshold: Minimum similarity score threshold (0-1)

        Returns:
            List of LangChain StructuredTool instances

        Raises:
            RuntimeError: If vector store is not initialized
            ValueError: If invalid k or threshold values

        Examples:
            tools = manager.get_tools("Get company financial ratios")
            tools = manager.get_tools("Find historical stock prices", k=5)
        """
        if not self.vector_store:
            raise RuntimeError(
                "Vector store not initialized. Call initialize_vector_store() first."
            )

        k = k or self.config.max_tools
        threshold = threshold or self.config.similarity_threshold

        if k < 1:
            raise ValueError("k must be >= 1")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")

        try:
            return self.vector_store.get_tools(query=query, k=k, threshold=threshold)
        except Exception as e:
            self.logger.error(f"Failed to get tools: {str(e)}")
            raise

    def search_endpoints(
        self, query: str, k: int = 3, threshold: float = 0.3
    ) -> list[dict]:
        """
        Search for relevant endpoints using natural language query.

        Args:
            query: Natural language query
            k: Maximum number of results to return
            threshold: Minimum similarity score threshold (0-1)

        Returns:
            List of dicts containing endpoint info with fields:
            - score: Similarity score
            - name: Endpoint name
            - description: Natural language description
            - category: Endpoint category
            - sub_category: Endpoint subcategory

        Raises:
            RuntimeError: If vector store is not initialized
            ValueError: If invalid k or threshold values

        Examples:
            results = manager.search_endpoints("Find company financials")
            for r in results:
                print(f"{r['name']}: {r['description']}")
        """
        if not self.vector_store:
            raise RuntimeError(
                "Vector store not initialized. Call initialize_vector_store() first."
            )

        k = k or self.config.max_tools
        threshold = threshold or self.config.similarity_threshold

        if k < 1:
            raise ValueError("k must be >= 1")
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")

        try:
            results = self.vector_store.search(query, k=k, threshold=threshold)
            return [
                {
                    "score": result.score,
                    "name": result.name,
                    "description": result.info.semantics.natural_description,
                    "category": result.info.semantics.category,
                    "sub_category": result.info.semantics.sub_category,
                }
                for result in results
            ]
        except Exception as e:
            self.logger.error(f"Failed to search endpoints: {str(e)}")
            raise
