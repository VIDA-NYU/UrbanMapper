from typing import Callable, Dict
import pandas as pd
from beartype import beartype
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator


AGGREGATION_FUNCTIONS: Dict[str, Callable[[pd.Series], float]] = {
    "mean": pd.Series.mean,
    "sum": pd.Series.sum,
    "median": pd.Series.median,
    "min": pd.Series.min,
    "max": pd.Series.max,
}


@beartype
class SimpleAggregator(BaseAggregator):
    """Aggregator For Standard Stats On Numeric Data.

    Applies stats functions (e.g., `mean`, `sum`) to `values` in a `column`, grouped by another.

    !!! tip "Useful for"
        Useful for scenarios like `average height` per district or `total population` per area.

    Supports predefined functions in `AGGREGATION_FUNCTIONS` or custom ones.

    !!! question "How to Use Custom Functions"
        Simply pass you own function receiving a series as parameter per the `aggregation_function` argument.
        Within the factory it'll be throughout `aggregate_by(.)` and `method` argument.

    Attributes:
        group_by_column: Column to group by.
        value_column: Column with values to aggregate.
        aggregation_function: Function to apply to grouped values.

    Examples:
        >>> import urban_mapper as um
        >>> import pandas as pd
        >>> mapper = um.UrbanMapper()
        >>> data = pd.DataFrame({
        ...     "district": ["A", "A", "B"],
        ...     "height": [10, 15, 20]
        ... })
        >>> enricher = mapper.enricher\
        ...     .with_data(group_by="district", values_from="height")\
        ...     .aggregate_by(method="mean", output_column="avg_height")\
        ...     .build()
    """

    def __init__(
        self,
        group_by_column: str,
        value_column: str,
        aggregation_function: Callable[[pd.Series], float],
    ) -> None:
        self.group_by_column = group_by_column
        self.value_column = value_column
        self.aggregation_function = aggregation_function

    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Aggregate data with the aggregation function.

        `Groups the DataFrame`, applies the function to `value_column`, and returns results.

        Args:
            input_dataframe: DataFrame with `group_by_column` and `value_column`.

        Returns:
            DataFrame with 'value' (aggregated values) and 'indices' (row indices).

        Raises:
            KeyError: If required columns are missing.
        """
        grouped = input_dataframe.groupby(self.group_by_column)
        aggregated = grouped[self.value_column].agg(self.aggregation_function)
        indices = grouped.apply(lambda g: list(g.index))
        return pd.DataFrame({"value": aggregated, "indices": indices})
