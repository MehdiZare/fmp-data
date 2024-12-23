# fmp_data/lc/manager.py
from copy import deepcopy

from langchain.tools import StructuredTool

from fmp_data import ClientConfig, FMPDataClient
from fmp_data.alternative.mapping import (
    ALTERNATIVE_ENDPOINT_MAP,
    ALTERNATIVE_ENDPOINTS_SEMANTICS,
)
from fmp_data.company.mapping import COMPANY_ENDPOINT_MAP, COMPANY_ENDPOINTS_SEMANTICS
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.setup import setup_vector_store
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger

logger = FMPLogger().get_logger(__name__)

ENDPOINT_GROUPS = [
    "alternative",
    "company",
    "market",
    "fundamental",
    "technical",
    "economics",
]


class FMPToolManager:
    def __init__(
        self,
        client: FMPDataClient | None = None,
        config: ClientConfig | None = None,
        store_name: str = "fmp_endpoints",
        auto_initialize: bool = True,
    ):
        """
        Initialize tool manager

        Args:
            client: Optional FMP API client
            config: Optional client configuration
            store_name: Name for vector store
            auto_initialize: Whether to automatically load endpoints
            and initialize vector store
        """
        self.config = config or ClientConfig.from_env()
        self.client = client or FMPDataClient(config=self.config)
        self.registry = EndpointRegistry()
        self.store_name = store_name
        self.vector_store: EndpointVectorStore | None = None

        # Initialize all groups to False
        self._loaded_groups = {group: False for group in ENDPOINT_GROUPS}

        if auto_initialize:
            self.load_all_endpoints()
            self.initialize_vector_store()

    def _register_endpoints(
        self, endpoint_map: dict[str, type], semantics_map: dict[str, type]
    ) -> None:
        """Register a group of endpoints with their semantics"""
        for name, endpoint in endpoint_map.items():
            try:
                # Get semantic name from the endpoint name
                semantic_name = name

                # Remove 'get_' prefix if present
                if semantic_name.startswith("get_"):
                    semantic_name = semantic_name[4:]

                # For search variants, use the full method name
                if "search" in semantic_name:
                    semantics = semantics_map.get(
                        semantic_name
                    )  # Use full name for search variants
                    if not semantics:
                        # Fallback to base search if specific variant not found
                        semantics = semantics_map.get("search")
                        logger.debug(f"Using base search semantics for {name}")
                else:
                    semantics = semantics_map.get(semantic_name)

                if not semantics:
                    logger.warning(
                        f"No semantics found for endpoint: {name} "
                        f"(semantic_name: {semantic_name})"
                    )
                    continue

                # Validate that method name matches between endpoint and semantics
                if semantics.method_name != name:
                    # Update method name in semantics to match endpoint
                    semantics = deepcopy(semantics)
                    semantics.method_name = name
                    logger.debug(
                        f"Updated method name in semantics "
                        f"from {semantics.method_name} "
                        f"to {name}"
                    )

                # Validate mandatory parameters have semantic hints
                mandatory_params = {p.name for p in endpoint.mandatory_params}
                semantic_hints = set(semantics.parameter_hints.keys())
                missing_hints = mandatory_params - semantic_hints

                if missing_hints:
                    logger.warning(
                        f"Missing semantic hints for mandatory parameters in "
                        f"{name}: {missing_hints}"
                    )

                self.registry.register(name, endpoint, semantics)
                logger.debug(
                    f"Successfully registered endpoint: {name} with "
                    f"{len(semantics.parameter_hints)} parameter hints"
                )

            except ValueError as e:
                logger.error(
                    f"Failed to register {name}: {str(e)}",
                    extra={"semantic_name": semantic_name},
                )
                raise
            except Exception as e:
                logger.error(
                    f"Unexpected error registering {name}: {str(e)}", exc_info=True
                )
                raise

    def load_alternative_endpoints(self) -> None:
        """Load alternative market endpoints"""
        if self._loaded_groups["alternative"]:
            logger.debug("Alternative endpoints already loaded")
            return

        try:
            self._register_endpoints(
                ALTERNATIVE_ENDPOINT_MAP, ALTERNATIVE_ENDPOINTS_SEMANTICS
            )
            self._loaded_groups["alternative"] = True
            logger.info("Successfully loaded alternative market endpoints")
        except Exception as e:
            logger.error(f"Failed to load alternative endpoints: {str(e)}")
            raise

    def load_company_endpoints(self) -> None:
        """Load company information endpoints"""
        if self._loaded_groups["company"]:
            logger.debug("Company endpoints already loaded")
            return

        try:
            self._register_endpoints(COMPANY_ENDPOINT_MAP, COMPANY_ENDPOINTS_SEMANTICS)
            self._loaded_groups["company"] = True
            logger.info("Successfully loaded company information endpoints")
        except Exception as e:
            logger.error(f"Failed to load company endpoints: {str(e)}")
            raise

    def load_all_endpoints(self) -> None:
        """Load all available endpoint groups"""
        loaded_count = 0

        try:
            # Load alternative markets
            self.load_alternative_endpoints()
            loaded_count += len(ALTERNATIVE_ENDPOINT_MAP)

            # Load company endpoints
            self.load_company_endpoints()
            loaded_count += len(COMPANY_ENDPOINT_MAP)

            logger.info(
                f"Successfully loaded {loaded_count} endpoints across "
                f"{sum(self._loaded_groups.values())} groups"
            )
        except Exception as e:
            logger.error(f"Failed to load all endpoints: {str(e)}")
            raise

    def _get_embeddings(self):
        """Get embeddings from config or raise error"""
        if not self.config.embedding:
            raise RuntimeError(
                "Embedding configuration not found. "
                "Please configure embeddings in client config or environment variables."
            )
        return self.config.embedding.get_embeddings()

    def initialize_vector_store(self, force_create: bool = False) -> None:
        """Initialize or load vector store"""
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

    def get_tools(
        self, query: str | None = None, k: int = 3, threshold: float = 0.3
    ) -> list[StructuredTool]:
        """
        Get relevant tools based on query

        Args:
            query: Natural language query to find relevant tools
            k: Number of tools to return
            threshold: Minimum similarity score threshold

        Returns:
            List of relevant LangChain tools
        """
        if not self.vector_store:
            raise RuntimeError(
                "Vector store not initialized. Call initialize_vector_store() first."
            )

        return self.vector_store.get_tools(query=query, k=k, threshold=threshold)

    def search_endpoints(
        self, query: str, k: int = 3, threshold: float = 0.3
    ) -> list[dict]:
        """
        Search for relevant endpoints

        Args:
            query: Natural language query
            k: Number of results to return
            threshold: Minimum similarity score threshold

        Returns:
            List of relevant endpoints with scores
        """
        if not self.vector_store:
            raise RuntimeError(
                "Vector store not initialized. Call initialize_vector_store() first."
            )

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
