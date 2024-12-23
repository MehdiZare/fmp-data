from pathlib import Path

from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import OpenAIEmbeddings

from fmp_data.base import BaseClient
from fmp_data.lc.registry import EndpointRegistry
from fmp_data.lc.vector_store import EndpointVectorStore
from fmp_data.logger import FMPLogger

logger = FMPLogger().get_logger(__name__)


class VectorStoreSetup:
    """Setup and management of endpoint vector store"""

    def __init__(
        self,
        client: BaseClient,
        registry: EndpointRegistry,
        embeddings: Embeddings | None = None,
        cache_dir: str | None = None,
        store_name: str = "default",
    ):
        self.client = client
        self.registry = registry
        self.embeddings = embeddings or self._get_default_embeddings()
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".fmp_cache"
        self.store_name = store_name

        # Setup paths
        self.store_dir = self.cache_dir / "vector_stores" / store_name
        self.store_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_path = self.store_dir / "metadata.json"
        self.index_path = self.store_dir / "faiss.index"

    def _get_default_embeddings(self) -> Embeddings:
        """Get default embeddings model"""
        # You can modify this to use different default embeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536,  # Specify dimensions explicitly for consistency
        )

    def _get_embedding_dimension(self) -> int:
        """Get embedding dimension by testing with a sample text"""
        sample_embedding = self.embeddings.embed_query("test")
        return len(sample_embedding)

    def store_exists(self) -> bool:
        """Check if vector store exists"""
        return self.metadata_path.exists() and self.index_path.exists()

    def validate_store(self) -> bool:
        """Validate existing vector store"""
        if not self.store_exists():
            return False

        try:
            # Try to load vector store
            vector_store = EndpointVectorStore(
                client=self.client,
                registry=self.registry,
                embeddings=self.embeddings,
                cache_dir=str(self.cache_dir),
                store_name=self.store_name,
            )

            # Check metadata
            metadata = vector_store.metadata
            expected_dimension = self._get_embedding_dimension()

            # Validate dimensions match
            if metadata.dimension != expected_dimension:
                logger.warning(
                    f"Dimension mismatch: stored={metadata.dimension}, "
                    f"expected={expected_dimension}"
                )
                return False

            # Validate all endpoints are present
            stored_endpoints = set(vector_store.vector_ids.values())
            registry_endpoints = set(self.registry.list_endpoints().keys())

            if stored_endpoints != registry_endpoints:
                missing = registry_endpoints - stored_endpoints
                extra = stored_endpoints - registry_endpoints
                if missing:
                    logger.warning(f"Missing endpoints in store: {missing}")
                if extra:
                    logger.warning(f"Extra endpoints in store: {extra}")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate vector store: {str(e)}")
            return False

    def create_store(self) -> EndpointVectorStore:
        """Create new vector store"""
        logger.info("Creating new vector store...")

        # Initialize store
        vector_store = EndpointVectorStore(
            client=self.client,
            registry=self.registry,
            embeddings=self.embeddings,
            cache_dir=str(self.cache_dir),
            store_name=self.store_name,
        )

        # Add all endpoints
        endpoint_names = list(self.registry.list_endpoints().keys())
        vector_store.add_endpoints(endpoint_names)

        # Save store
        vector_store.save()
        logger.info(f"Created vector store with {len(endpoint_names)} endpoints")

        return vector_store

    def setup(self) -> EndpointVectorStore:
        """Setup vector store, creating new one if needed"""
        if self.store_exists():
            logger.info("Found existing vector store")
            if self.validate_store():
                logger.info("Existing store is valid")
                return EndpointVectorStore(
                    client=self.client,
                    registry=self.registry,
                    embeddings=self.embeddings,
                    cache_dir=str(self.cache_dir),
                    store_name=self.store_name,
                )
            else:
                logger.warning("Existing store is invalid, creating new one")

        return self.create_store()


def setup_vector_store(
    client: BaseClient,
    registry: EndpointRegistry,
    embeddings: Embeddings | None = None,
    cache_dir: str | None = None,
    store_name: str = "default",
    force_create: bool = False,
) -> EndpointVectorStore:
    """
    Setup vector store with provided configuration

    Args:
        client: FMP API client
        registry: Endpoint registry
        embeddings: Optional embeddings model
        cache_dir: Optional cache directory
        store_name: Name for the vector store
        force_create: Whether to force creation of new store

    Returns:
        Configured vector store
    """
    setup = VectorStoreSetup(
        client=client,
        registry=registry,
        embeddings=embeddings,
        cache_dir=cache_dir,
        store_name=store_name,
    )

    if force_create:
        return setup.create_store()

    return setup.setup()
