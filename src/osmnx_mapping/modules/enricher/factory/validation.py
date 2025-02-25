from .config import EnricherConfig
from .registries import ENRICHER_REGISTRY
from osmnx_mapping.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)


def validate_group_by(config: EnricherConfig):
    if not config.group_by:
        raise ValueError("Missing group_by. Use with_data() to set it.")


def validate_action(config: EnricherConfig):
    if not config.action:
        raise ValueError("No action specified. Use aggregate_with() or count_by().")


def validate_aggregation_method(method: str):
    if method not in AGGREGATION_FUNCTIONS:
        raise ValueError(
            f"Unknown aggregation method '{method}'. Available: {list(AGGREGATION_FUNCTIONS.keys())}"
        )


def validate_enricher_type(enricher_type: str):
    if enricher_type not in ENRICHER_REGISTRY:
        raise ValueError(
            f"Unknown enricher type '{enricher_type}'. Available: {list(ENRICHER_REGISTRY.keys())}"
        )
