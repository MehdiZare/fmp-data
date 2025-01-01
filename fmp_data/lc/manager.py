# fmp_data/lc/manager.py

from langchain.tools import StructuredTool

from fmp_data import ClientConfig, ConfigError, FMPDataClient
from fmp_data.lc.mapping import ENDPOINT_GROUPS
from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.registry import Endpoint, EndpointRegistry
from fmp_data.lc.setup import setup_vector_store
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger

logger = FMPLogger().get_logger(__name__)


class FMPToolManager:
    """
    Manager for FMP API tools and endpoints with LangChain integration.

    Provides natural language search and tool creation for FMP API endpoints.
    Handles endpoint registration, validation, and vector store management.

    Args:
        client: FMPDataClient instance or None (will create from config if None)
        config: ClientConfig instance or None (will load from env if None)
        store_name: Name for the vector store
        auto_initialize: Whether to initialize endpoints and store on creation

    Examples:
        # Create with default settings
        manager = FMPToolManager()

        # Get tools for a specific query
        tools = manager.get_tools("Get company financial ratios")

        # Search for relevant endpoints
        results = manager.search_endpoints("Find historical stock prices")
    """

    def __init__(
        self,
        client: FMPDataClient | None = None,
        config: ClientConfig | None = None,
        store_name: str = "fmp_endpoints",
        auto_initialize: bool = True,
        endpoint_groups: dict[str, dict] = ENDPOINT_GROUPS,
    ):
        try:
            self.config = config or ClientConfig.from_env()
            self.client = client or FMPDataClient(config=self.config)
            self.registry = EndpointRegistry()
            self.store_name = store_name
            self.endpoint_groups = endpoint_groups
            self.vector_store: EndpointVectorStore | None = None
            self._loaded_groups = {
                group: False for group in self.endpoint_groups.keys()
            }
            self.logger = FMPLogger().get_logger(self.__class__.__name__)

            if auto_initialize:
                self.initialize()
        except Exception as e:
            raise ConfigError(f"Failed to initialize FMP Tool Manager: {str(e)}") from e

    def initialize(self) -> None:
        """Initialize endpoints and vector store"""
        try:
            logger.info("Initializing FMP Tool Manager")
            self.load_all_endpoints()

            if not self.registry.list_endpoints():
                raise RuntimeError("No endpoints were registered during initialization")

            # Then initialize vector store
            embeddings = self._get_embeddings()
            self.vector_store = setup_vector_store(
                client=self.client,
                registry=self.registry,
                embeddings=embeddings,
                store_name=self.store_name,
            )

            if not self.vector_store:
                raise RuntimeError("Failed to initialize vector store")

        except Exception as e:
            self.logger.error("Failed to initialize tool manager", exc_info=True)
            raise ConfigError(f"Initialization failed: {str(e)}") from e

    def initialize_vector_store(self, force_create: bool = False) -> None:
        """Initialize or load vector store"""
        if self.vector_store is not None and not force_create:
            logger.debug("Vector store already initialized")
            return

        embeddings = self._get_embeddings()

        self.vector_store = setup_vector_store(
            client=self.client,
            registry=self.registry,
            embeddings=embeddings,
            store_name=self.store_name,
            force_create=force_create,
        )
        logger.info(
            f"Initialized vector store with "
            f"{len(self.registry.list_endpoints())} endpoints"
        )

    def _register_endpoints(
        self,
        endpoint_map: dict[str, Endpoint],
        semantics_map: dict[str, EndpointSemantics],
    ) -> tuple[int, set[str], set[str]]:
        registered = set()
        skipped = set()

        for name, endpoint in endpoint_map.items():
            try:
                semantic_name = name[4:] if name.startswith("get_") else name

                # Special debug for problematic endpoint
                if name == "get_financial_reports_dates":
                    self.logger.debug(f"Processing {name}:")
                    self.logger.debug(f"  Semantic name: {semantic_name}")
                    self.logger.debug(
                        f"  Available semantics: {list(semantics_map.keys())}"
                    )
                    self.logger.debug(
                        f"  Found in semantics: {semantic_name in semantics_map}"
                    )
                    # Print category information
                    if semantics_map.get(semantic_name):
                        self.logger.debug(
                            f"  Category: {semantics_map[semantic_name].category}"
                        )

                semantics = semantics_map.get(semantic_name)
                if not semantics:
                    self.logger.debug(
                        f"No semantics found for endpoint {name} "
                        f"(semantic_name: {semantic_name})"
                    )
                    skipped.add(name)
                    continue

                # Debug validation
                if name == "get_financial_reports_dates":
                    valid, msg = self.registry._validation.validate_category(
                        name, semantics.category
                    )
                    self.logger.debug(f"  Validation result: {valid}, {msg}")

                # Rest of the registration code...

                self.registry.register(name, endpoint, semantics)
                registered.add(name)

            except Exception as e:
                self.logger.error(f"Failed to register {name}: {str(e)}", exc_info=True)
                skipped.add(name)

        return len(registered), registered, skipped

    def load_endpoints(
        self, endpoint_map: dict, semantics_map: dict, group_name: str
    ) -> tuple[int, set[str], set[str]]:
        """Load endpoints for a specific group"""
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

            # Log summary of registration results
            if all_skipped:
                self.logger.warning(
                    f"Failed to register {len(all_skipped)} "
                    f"endpoints: {sorted(all_skipped)}"
                )

            self.logger.info(
                f"Successfully registered {len(all_registered)} endpoints across "
                f"{len(loaded_groups)} groups: {', '.join(loaded_groups)}"
            )

            # Detailed registration statistics at debug level
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
