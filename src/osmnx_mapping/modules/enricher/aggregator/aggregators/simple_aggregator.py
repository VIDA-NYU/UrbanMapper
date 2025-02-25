from typing import Callable
import pandas as pd
from beartype import beartype
from osmnx_mapping.modules.enricher.aggregator.abc_aggregator import BaseAggregator

from typing import Dict

from osmnx_mapping.utils import require_attribute_columns

AGGREGATION_FUNCTIONS: Dict[str, Callable[[pd.Series], float]] = {
    "mean": pd.Series.mean,
    "sum": pd.Series.sum,
    "median": pd.Series.median,
    "min": pd.Series.min,
    "max": pd.Series.max,
}


class SimpleAggregator(BaseAggregator):
    @beartype
    def __init__(
        self,
        group_by_column: str,
        value_column: str,
        aggregation_function: Callable[[pd.Series], float],
    ) -> None:
        self.group_by_column = group_by_column
        self.value_column = value_column
        self.aggregation_function = aggregation_function

    @beartype
    @require_attribute_columns("input_dataframe", ["group_by_column", "value_column"])
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series:
        return input_dataframe.groupby(self.group_by_column)[self.value_column].agg(
            self.aggregation_function
        )
