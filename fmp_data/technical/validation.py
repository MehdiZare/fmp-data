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

    # Must match the parent type EXACTLY:
    PARAMETER_PATTERNS: ClassVar[
        dict[str, list[str] | dict[str, list[str] | str | int]]
    ] = {
        # Each top-level key is either a list[str] or a dict[str, list[str]|str|int]
        "symbol": [r"^[A-Z]{1,5}$"],
        "interval": [r"^(1min|5min|15min|30min|1hour|4hour|daily)$"],
        "date": [r"^\d{4}-\d{2}-\d{2}$"],
        "period": [r"^([1-9]|[1-9][0-9]|1[0-9][0-9]|200)$"],
        "volatility_specific": {"std_dev": [r"^([1-9]|10)$"]},
        "kama_specific": {"acceleration": [r"^0?\.[0-9]+$|^1\.0*$"]},
        "momentum_specific": {
            "slow_period": [r"^([1-9]|[1-9][0-9]|100)$"],
            "fast_period": [r"^([1-9]|[1-4][0-9]|50)$"],
            "signal_period": [r"^([1-9]|[1-4][0-9]|50)$"],
        },
    }

    REQUIRED_PARAMS: ClassVar[dict[str, set[str]]] = {
        "Moving Averages": {"symbol", "period"},
        "Oscillators": {"symbol", "period"},
        "Momentum": {"symbol", "period"},
        "Volatility": {"symbol", "period"},
        "Volume": {"symbol"},
    }

    @property
    def expected_category(self) -> SemanticCategory:
        return SemanticCategory.TECHNICAL_ANALYSIS

    def get_parameter_requirements(
        self, method_name: str
    ) -> dict[str, list[str]] | None:
        """
        Return a dictionary of parameter regex lists for recognized endpoints.
        E.g. "get_sma" => {"symbol": [...], "interval": [...], "period": [...]}
        If 'method_name' does not match any subcategory or operation, return None.
        """
        endpoint_info = self.get_endpoint_info(method_name)
        if not endpoint_info:
            return None

        subcategory, operation = endpoint_info
        base_patterns: dict[str, list[str]] = {}

        # Always add symbol + interval if available
        self._add_top_level_pattern("symbol", base_patterns)
        self._add_top_level_pattern("interval", base_patterns)

        # Some subcategories require 'period'
        if subcategory in {"Moving Averages", "Oscillators", "Momentum", "Volatility"}:
            self._add_top_level_pattern("period", base_patterns)

        # operation-based logic
        match operation:
            case "bbands":
                self._add_subdict_patterns("volatility_specific", base_patterns)
            case "kama":
                self._add_subdict_patterns("kama_specific", base_patterns)
            case "macd" | "ppo":
                self._add_subdict_patterns("momentum_specific", base_patterns)
            # etc. for other indicators if needed

        return base_patterns if base_patterns else None

    def _add_top_level_pattern(
        self, key: str, base_patterns: dict[str, list[str]]
    ) -> None:
        """
        If the top-level PARAMETER_PATTERNS[key] is a list, copy it into base_patterns.
        """
        pattern_value = self.PARAMETER_PATTERNS.get(key)
        if isinstance(pattern_value, list):
            base_patterns[key] = pattern_value

    def _add_subdict_patterns(
        self, dict_key: str, base_patterns: dict[str, list[str]]
    ) -> None:
        """
        If PARAMETER_PATTERNS[dict_key] is a dict, copy any list[str] entries
        into base_patterns.
        E.g. volatility_specific = {"std_dev": [r"..."], ...}
        """
        sub_dict = self.PARAMETER_PATTERNS.get(dict_key)
        if isinstance(sub_dict, dict):
            for sub_key, sub_val in sub_dict.items():
                if isinstance(sub_val, list):
                    base_patterns[sub_key] = sub_val
