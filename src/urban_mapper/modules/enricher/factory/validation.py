from .config import EnricherConfig
from urban_mapper.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)


def validate_group_by(config: EnricherConfig) -> None:
    """Ensure `group_by` is set in the config.

    Args:
        config: Enricher config to check.

    Raises:
        ValueError: If group_by isn’t set.
    """
    if not config.group_by:
        raise ValueError("Missing group_by. Use with_data() to set it.")


def validate_action(config: EnricherConfig) -> None:
    """Ensure an action is specified.

    Args:
        config: Enricher config to check.

    Raises:
        ValueError: If no action is set.
    """
    if not config.action:
        raise ValueError("No action specified. Use aggregate_with() or count_by().")


def validate_aggregation_method(method: str) -> None:
    """Check if the aggregation method is valid.

    Args:
        method: Aggregation method name to validate.

    Raises:
        ValueError: If method isn’t in AGGREGATION_FUNCTIONS.
    """
    if method not in AGGREGATION_FUNCTIONS:
        raise ValueError(
            f"Unknown aggregation method '{method}'. Available: {list(AGGREGATION_FUNCTIONS.keys())}"
        )
