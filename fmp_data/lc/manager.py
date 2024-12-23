# fmp_data/lc/manager.py

from langchain.tools import StructuredTool

from fmp_data import ClientConfig, FMPDataClient

# Import endpoint maps and semantics from different modules
from fmp_data.alternative.mapping import (
    ALTERNATIVE_ENDPOINT_MAP,
    ALTERNATIVE_ENDPOINTS_SEMANTICS,
)
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.setup import setup_vector_store
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger

# Add other endpoint imports as needed
# from fmp_data.market.mapping import MARKET_ENDPOINT_MAP, MARKET_ENDPOINTS_SEMANTICS
# etc.

logger = FMPLogger().get_logger(__name__)


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

        # Map to track loaded endpoint groups
        self._loaded_groups = {
            "alternative": False,
            "market": False,
            "fundamental": False,
            # Add other groups as needed
        }

        if auto_initialize:
            self.load_all_endpoints()
            self.initialize_vector_store()

    def _register_endpoints(
        self, endpoint_map: dict[str, type], semantics_map: dict[str, type]
    ) -> None:
        """Register a group of endpoints with their semantics"""
        for name, endpoint in endpoint_map.items():
            semantic_name = name.replace("get_", "")
            semantics = semantics_map.get(semantic_name)

            if not semantics:
                logger.warning(f"No semantics found for endpoint: {name}")
                continue

            try:
                self.registry.register(name, endpoint, semantics)
                logger.debug(f"Registered endpoint: {name}")
            except ValueError as e:
                logger.error(f"Failed to register {name}: {str(e)}")
                raise

    def load_alternative_endpoints(self) -> None:
        """Load alternative market endpoints"""
        if self._loaded_groups["alternative"]:
            return

        self._register_endpoints(
            ALTERNATIVE_ENDPOINT_MAP, ALTERNATIVE_ENDPOINTS_SEMANTICS
        )
        self._loaded_groups["alternative"] = True
        logger.info("Loaded alternative market endpoints")

    def load_all_endpoints(self) -> None:
        """Load all available endpoint groups"""
        # Load alternative markets
        self.load_alternative_endpoints()
        logger.info("Loaded all available endpoints")

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
