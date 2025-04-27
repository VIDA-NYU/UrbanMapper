"""
Aggregator module for the UrbanMapper enrichment system.

This module provides aggregator classes for performing statistical operations
on grouped data within the UrbanMapper framework. Aggregators are used by
enrichers to process and transform data, producing summary statistics and
counts that can be mapped to urban features.

The module includes:

- BaseAggregator: Abstract base class defining the aggregator interface
- SimpleAggregator: Performs standard statistical operations (mean, sum, etc.)
- CountAggregator: Counts records, optionally with custom counting functions

These aggregators are primarily used by the enricher component to perform
spatial enrichment operations, such as counting points within regions,
calculating average values for areas, and similar geospatial analyses.

Examples:
    >>> from urban_mapper.modules.enricher.aggregator import SimpleAggregator, AGGREGATION_FUNCTIONS
    >>>
    >>> # Create an aggregator to calculate mean building heights by district
    >>> aggregator = SimpleAggregator(
    ...     group_by_column='district',
    ...     value_column='building_height',
    ...     aggregation_function=AGGREGATION_FUNCTIONS['mean']
    ... )
    >>>
    >>> # Apply to a DataFrame
    >>> result = aggregator.aggregate(data)
"""

from .aggregators import SimpleAggregator, CountAggregator, AGGREGATION_FUNCTIONS
from .abc_aggregator import BaseAggregator

__all__ = [
    "SimpleAggregator",
    "CountAggregator",
    "BaseAggregator",
    "AGGREGATION_FUNCTIONS",
]
