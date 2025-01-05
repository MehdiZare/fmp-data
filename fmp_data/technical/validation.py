from typing import ClassVar

from fmp_data.lc.models import SemanticCategory
from fmp_data.lc.validation import CommonValidationRule


class TechnicalAnalysisRule(CommonValidationRule):
    """Validation rules for technical analysis endpoints"""

    METHOD_GROUPS: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "Moving Averages": (
            "get_",
            ["sma", "ema", "wma", "dema", "tema", "trima", "kama", "mama"],
        ),
        "Oscillators": (
            "get_",
            ["williams", "rsi", "stoch", "stochrsi", "macd", "ppo", "roc"],
        ),
        "Momentum": (
            "get_",
            ["adx", "cci", "mfi", "mom", "dx"],
        ),
        "Volatility": (
            "get_",
            ["standard_deviation", "atr", "natr", "bbands"],
        ),
        "Volume": (
            "get_",
            ["obv", "ad", "adosc"],
        ),
    }

    PARAMETER_PATTERNS: ClassVar[dict[str, dict[str, list[str] | str | int]]] = {
        # Common patterns
        "symbol": [r"^[A-Z]{1,5}$"],
        "interval": [r"^(1min|5min|15min|30min|1hour|4hour|daily)$"],
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        "period": [r"^([1-9]|[1-9][0-9]|1[0-9][0-9]|200)$"],  # 1-200
        # Specific indicator patterns
        "volatility_specific": {"std_dev": [r"^([1-9]|10)$"]},  # 1-10
        "kama_specific": {"acceleration": [r"^0?\.[0-9]+$|^1\.0*$"]},  # 0-1
        "momentum_specific": {
            "slow_period": [r"^([1-9]|[1-9][0-9]|100)$"],  # 1-100
            "fast_period": [r"^([1-9]|[1-4][0-9]|50)$"],  # 1-50
            "signal_period": [r"^([1-9]|[1-4][0-9]|50)$"],  # 1-50
        },
    }

    # Required parameters by indicator type
    REQUIRED_PARAMS: ClassVar[dict[str, set[str]]] = {
        "Moving Averages": {"symbol", "period"},
        "Oscillators": {"symbol", "period"},
        "Momentum": {"symbol", "period"},
        "Volatility": {"symbol", "period"},
        "Volume": {"symbol"},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        """Category for technical analysis endpoints"""
        return SemanticCategory.TECHNICAL_ANALYSIS

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """Get parameter validation patterns with technical-specific logic"""
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info

        # Base requirements
        base_patterns = {
            "symbol": self.PARAMETER_PATTERNS["symbol"],
            "interval": self.PARAMETER_PATTERNS["interval"],
        }

        # Add period requirement for applicable subcategories
        if subcategory in ["Moving Averages", "Oscillators", "Momentum", "Volatility"]:
            base_patterns["period"] = self.PARAMETER_PATTERNS["period"]

        # Add operation-specific patterns
        match operation:
            case "bbands":
                base_patterns.update(self.PARAMETER_PATTERNS["volatility_specific"])
            case "kama":
                base_patterns.update(self.PARAMETER_PATTERNS["kama_specific"])
            case "macd" | "ppo":
                base_patterns.update(self.PARAMETER_PATTERNS["momentum_specific"])

        return base_patterns
