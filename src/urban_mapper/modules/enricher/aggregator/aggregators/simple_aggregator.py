from typing import Callable
import pandas as pd
from beartype import beartype
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator

from typing import Dict


AGGREGATION_FUNCTIONS: Dict[str, Callable[[pd.Series], float]] = {
    "mean": pd.Series.mean,
    "sum": pd.Series.sum,
    "median": pd.Series.median,
    "min": pd.Series.min,
    "max": pd.Series.max,
}


@beartype
class SimpleAggregator(BaseAggregator):
    def __init__(
        self,
        group_by_column: str,
        value_column: str,
        aggregation_function: Callable[[pd.Series], float],
    ) -> None:
        self.group_by_column = group_by_column
        self.value_column = value_column
        self.aggregation_function = aggregation_function

    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series:
        grouped = input_dataframe.groupby(self.group_by_column)
        aggregated = grouped[self.value_column].agg(self.aggregation_function)
        return aggregated
