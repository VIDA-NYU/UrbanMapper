"""
Concrete aggregator implementations for the UrbanMapper enrichment system.

This module provides the concrete implementations of the BaseAggregator abstract
class, each implementing a specific type of aggregation operation:

- SimpleAggregator: Applies standard statistical functions to grouped data
- CountAggregator: Counts records within each group, optionally with conditions

It also exports the AGGREGATION_FUNCTIONS dictionary, which provides convenient
access to common aggregation functions (mean, sum, min, max, etc.).
"""

from .simple_aggregator import SimpleAggregator, AGGREGATION_FUNCTIONS
from .count_aggregator import CountAggregator

__all__ = ["SimpleAggregator", "CountAggregator", "AGGREGATION_FUNCTIONS"]
