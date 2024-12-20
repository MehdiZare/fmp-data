# fmp_langchain/endpoints/__init__.py
from fmp_data.lc.models import ALTERNATIVE_ENDPOINTS
from fmp_data.lc.utils import is_langchain_available

is_langchain_available()

# Import other endpoint definitions as they're created

# Combine all endpoint definitions
ALL_ENDPOINT_SEMANTICS = {
    **ALTERNATIVE_ENDPOINTS,
    # Add other endpoint categories as they're created
}
