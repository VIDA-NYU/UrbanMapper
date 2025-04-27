from typing import Callable, Any
import pandas as pd
from beartype import beartype
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator
from urban_mapper.utils.helpers import require_attribute_columns


@beartype
class CountAggregator(BaseAggregator):
    """Aggregator For Counting Records In Groups.

    Counts records per group, with an optional custom counting function. By default,
    it uses `len()` to count all records, but you can tweak it to count specific cases, see below.

    !!! tip "Useful for"

        - [x] Counting taxi pickups per area
        - [x] Tallying incidents per junction
        - [x] Totting up points of interest per district

    Attributes:
        group_by_column: Column to group data by.
        count_function: Function to count records in each group (defaults to len).

    Examples:
        >>> import urban_mapper as um
        >>> import pandas as pd
        >>> mapper = um.UrbanMapper()
        >>> data = pd.DataFrame({
        ...     "junction": ["A", "A", "B", "B", "C"],
        ...     "type": ["minor", "major", "minor", "major", "minor"]
        ... })
        >>> enricher = mapper.enricher\
        ...     .with_data(group_by="junction")\
        ...     .count_by(output_column="incident_count")\
        ...     .build()
    """

    def __init__(
        self,
        group_by_column: str,
        count_function: Callable[[pd.DataFrame], Any] = len,
    ) -> None:
        self.group_by_column = group_by_column
        self.count_function = count_function

    @require_attribute_columns("input_dataframe", ["group_by_column"])
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Count records per group using the count function.

        Groups the DataFrame by `group_by_column`, applies the count function,
        and returns a DataFrame with counts and indices.

        Args:
            input_dataframe: DataFrame to aggregate, must have `group_by_column`.

        Returns:
            DataFrame with 'value' (counts) and 'indices' (original row indices).

        Raises:
            ValueError: If required column is missing.
        """
        grouped = input_dataframe.groupby(self.group_by_column)
        values = grouped.apply(self.count_function)
        indices = grouped.apply(lambda g: list(g.index))
        return pd.DataFrame({"value": values, "indices": indices})
