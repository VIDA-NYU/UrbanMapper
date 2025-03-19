from __future__ import annotations
from typing import Type, Dict
from beartype import beartype
from urban_mapper.modules.enricher.abc_enricher import EnricherBase
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator

ENRICHER_REGISTRY: Dict[str, Type[EnricherBase]] = {}
AGGREGATOR_REGISTRY: Dict[str, Type[BaseAggregator]] = {}


@beartype
def register_enricher(name: str, enricher_class: Type[EnricherBase]) -> None:
    if not issubclass(enricher_class, EnricherBase):
        raise TypeError(f"{enricher_class.__name__} must subclass EnricherBase")
    ENRICHER_REGISTRY[name] = enricher_class


@beartype
def register_aggregator(name: str, aggregator_class: Type[BaseAggregator]) -> None:
    if not issubclass(aggregator_class, BaseAggregator):
        raise TypeError(f"{aggregator_class.__name__} must subclass BaseAggregator")
    AGGREGATOR_REGISTRY[name] = aggregator_class
