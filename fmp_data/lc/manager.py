# fmp_data/lc/manager.py
from copy import deepcopy

from investment.mapping import INVESTMENT_ENDPOINT_MAP, INVESTMENT_ENDPOINTS_SEMANTICS
from langchain.tools import StructuredTool

from fmp_data import ClientConfig, FMPDataClient
from fmp_data.alternative.mapping import (
    ALTERNATIVE_ENDPOINT_MAP,
    ALTERNATIVE_ENDPOINTS_SEMANTICS,
)
from fmp_data.company.mapping import COMPANY_ENDPOINT_MAP, COMPANY_ENDPOINTS_SEMANTICS
from fmp_data.economics.mapping import (
    ECONOMICS_ENDPOINT_MAP,
    ECONOMICS_ENDPOINTS_SEMANTICS,
)
from fmp_data.fundamental.mapping import (
    FUNDAMENTAL_ENDPOINT_MAP,
    FUNDAMENTAL_ENDPOINTS_SEMANTICS,
)
from fmp_data.institutional.mapping import (
    INSTITUTIONAL_ENDPOINT_MAP,
    INSTITUTIONAL_ENDPOINTS_SEMANTICS,
)
from fmp_data.intelligence.mapping import (
    INTELLIGENCE_ENDPOINT_MAP,
    INTELLIGENCE_ENDPOINTS_SEMANTICS,
)
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
    "institutional",
    "intelligence",
    "investment",
]


class FMPToolManager:
    ENDPOINT_GROUPS = {
        "alternative": {
            "endpoint_map": ALTERNATIVE_ENDPOINT_MAP,
            "semantics_map": ALTERNATIVE_ENDPOINTS_SEMANTICS,
            "display_name": "alternative market",
        },
        "company": {
            "endpoint_map": COMPANY_ENDPOINT_MAP,
            "semantics_map": COMPANY_ENDPOINTS_SEMANTICS,
            "display_name": "company information",
        },
        "economics": {
            "endpoint_map": ECONOMICS_ENDPOINT_MAP,
            "semantics_map": ECONOMICS_ENDPOINTS_SEMANTICS,
            "display_name": "economics data",
        },
        "fundamental": {
            "endpoint_map": FUNDAMENTAL_ENDPOINT_MAP,
            "semantics_map": FUNDAMENTAL_ENDPOINTS_SEMANTICS,
            "display_name": "fundamental analysis",
        },
        "institutional": {
            "endpoint_map": INSTITUTIONAL_ENDPOINT_MAP,
            "semantics_map": INSTITUTIONAL_ENDPOINTS_SEMANTICS,
            "display_name": "institutional data",
        },
        "intelligence": {
            "endpoint_map": INTELLIGENCE_ENDPOINT_MAP,
            "semantics_map": INTELLIGENCE_ENDPOINTS_SEMANTICS,
            "display_name": "market intelligence",
        },
        "investment": {
            "endpoint_map": INVESTMENT_ENDPOINT_MAP,
            "semantics_map": INVESTMENT_ENDPOINTS_SEMANTICS,
            "display_name": "investment",
        },
    }

    def __init__(
        self,
        client: FMPDataClient | None = None,
        config: ClientConfig | None = None,
        store_name: str = "fmp_endpoints",
        auto_initialize: bool = True,
    ):
        self.config = config or ClientConfig.from_env()
        self.client = client or FMPDataClient(config=self.config)
        self.registry = EndpointRegistry()
        self.store_name = store_name
        self.vector_store: EndpointVectorStore | None = None
        self._loaded_groups = {group: False for group in self.ENDPOINT_GROUPS.keys()}

        if auto_initialize:
            self.initialize()

    def initialize(self) -> None:
        """Initialize endpoints and vector store"""
        # First load all endpoints
        logger.info("Initializing FMP Tool Manager")
        self.load_all_endpoints()

        # Then initialize vector store
        embeddings = self._get_embeddings()
        self.vector_store = setup_vector_store(
            client=self.client,
            registry=self.registry,
            embeddings=embeddings,
            store_name=self.store_name,
        )

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
        self, endpoint_map: dict[str, type], semantics_map: dict[str, type]
    ) -> None:
        """Register a group of endpoints with their semantics"""
        registered = 0
        skipped = 0
        skipped_endpoints = set()

        for name, endpoint in endpoint_map.items():
            try:
                # Get semantic name from the endpoint name
                semantic_name = (
                    name.replace("get_", "") if name.startswith("get_") else name
                )

                semantics = semantics_map.get(semantic_name)
                if not semantics:
                    logger.warning(
                        f"No semantics found for endpoint: {name} "
                        f"(semantic_name: {semantic_name})"
                    )
                    skipped += 1
                    skipped_endpoints.add(name)
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
                registered += 1
                logger.debug(
                    f"Successfully registered endpoint: {name} with "
                    f"{len(semantics.parameter_hints)} parameter hints"
                )

            except Exception as e:
                logger.error(f"Failed to register {name}: {str(e)}", exc_info=True)
                skipped += 1
                skipped_endpoints.add(name)

        logger.debug(
            f"Registration summary: {registered} registered, {skipped} skipped"
        )
        if skipped_endpoints:
            logger.debug(f"Skipped endpoints: {skipped_endpoints}")

    def load_endpoints(
        self, endpoint_map: dict, semantics_map: dict, group_name: str
    ) -> tuple[int, set[str]]:
        """Load endpoints for a specific group"""
        try:
            self._register_endpoints(endpoint_map, semantics_map)
            # Remove success logging from here - we'll log once at the end
            return len(endpoint_map), set(endpoint_map.keys())
        except Exception as e:
            logger.error(f"Failed to load {group_name} endpoints: {str(e)}")
            raise

    def load_all_endpoints(self) -> None:
        """Load all available endpoint groups"""
        total_count = 0
        all_endpoints = set()
        loaded_groups = []

        try:
            for group_name, config in self.ENDPOINT_GROUPS.items():
                if self._loaded_groups.get(group_name):
                    continue

                count, endpoints = self.load_endpoints(
                    config["endpoint_map"], config["semantics_map"], group_name
                )
                self._loaded_groups[group_name] = True
                total_count += count
                all_endpoints.update(endpoints)
                loaded_groups.append(config["display_name"])

            # Get actually registered endpoints
            registered_endpoints = set(self.registry.list_endpoints().keys())
            missing_endpoints = all_endpoints - registered_endpoints

            # Single summary log at the end
            if missing_endpoints:
                logger.warning(f"Missing semantics for endpoints: {missing_endpoints}")

            logger.info(
                f"Loaded {len(registered_endpoints)} endpoints "
                f"across {len(loaded_groups)} groups: {', '.join(loaded_groups)}"
            )
        except Exception as e:
            logger.error(f"Failed to load endpoints: {str(e)}")
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
