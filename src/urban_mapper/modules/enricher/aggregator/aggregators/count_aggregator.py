from typing import Callable
import pandas as pd
from beartype import beartype
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator
from urban_mapper.utils.helpers import require_attribute_columns


@beartype
class CountAggregator(BaseAggregator):
    def __init__(
        self,
        group_by_column: str,
        count_function: Callable[[pd.core.groupby.GroupBy], float] = len,
    ) -> None:
        self.group_by_column = group_by_column
        self.count_function = count_function

    @require_attribute_columns("input_dataframe", ["group_by_column"])
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series:
        grouped = input_dataframe.groupby(self.group_by_column)

        return pd.Series(
            {
                group_name: self.count_function(group_data)
                for group_name, group_data in grouped
            },
            name="count",
        )
