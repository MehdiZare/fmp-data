# fmp_data/lc/manager.py

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
from fmp_data.investment.mapping import (
    INVESTMENT_ENDPOINT_MAP,
    INVESTMENT_ENDPOINTS_SEMANTICS,
)
from fmp_data.lc.models import EndpointSemantics
from fmp_data.lc.registry import Endpoint, EndpointRegistry
from fmp_data.lc.setup import setup_vector_store
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger
from fmp_data.market.mapping import MARKET_ENDPOINT_MAP, MARKET_ENDPOINTS_SEMANTICS
from fmp_data.technical.mapping import (
    TECHNICAL_ENDPOINT_MAP,
    TECHNICAL_ENDPOINTS_SEMANTICS,
)

logger = FMPLogger().get_logger(__name__)

ENDPOINT_GROUPS = [
    "alternative",
    "company",
    "economics",
    "fundamental",
    "institutional",
    "intelligence",
    "investment",
    "market",
    "technical",
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
        "market": {
            "endpoint_map": MARKET_ENDPOINT_MAP,
            "semantics_map": MARKET_ENDPOINTS_SEMANTICS,
            "display_name": "market",
        },
        "technical": {
            "endpoint_map": TECHNICAL_ENDPOINT_MAP,
            "semantics_map": TECHNICAL_ENDPOINTS_SEMANTICS,
            "display_name": "technical analysis",
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
        self.logger = FMPLogger().get_logger(self.__class__.__name__)

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
        """
        Load endpoints for a specific group
        """
        try:
            # Add debug logging
            if group_name == "intelligence":
                self.logger.debug("Intelligence endpoints:")
                self.logger.debug(f"  Endpoint map keys: {sorted(endpoint_map.keys())}")
                self.logger.debug(
                    f"  Semantics map keys: {sorted(semantics_map.keys())}"
                )

                # Look for our problematic endpoint
                if "get_financial_reports_dates" in endpoint_map:
                    self.logger.debug(
                        "Found get_financial_reports_dates in endpoint map"
                    )
                    semantic_name = "financial_reports_dates"
                    self.logger.debug(f"Looking for {semantic_name} in semantics")
                    self.logger.debug(f"Found: {semantic_name in semantics_map}")

            return self._register_endpoints(endpoint_map, semantics_map)
        except Exception as e:
            self.logger.error(
                f"Failed to load {group_name} endpoints: {str(e)}", exc_info=True
            )
            raise

    def load_all_endpoints(self) -> None:
        """Load all available endpoint groups"""
        total_registered = 0
        all_registered = set()
        all_skipped = set()
        loaded_groups = []

        try:
            for group_name, config in self.ENDPOINT_GROUPS.items():
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
            self.logger.debug(
                "Registration details",
                extra={
                    "registered": len(all_registered),
                    "skipped": len(all_skipped),
                    "total_attempted": len(all_registered) + len(all_skipped),
                    "success_rate": f"{(len(all_registered) /
                            (len(all_registered) + len(all_skipped)) * 100):.1f}%",
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
