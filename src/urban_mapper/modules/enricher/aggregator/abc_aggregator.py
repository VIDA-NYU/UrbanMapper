from abc import ABC, abstractmethod
import pandas as pd
from beartype import beartype
from urban_mapper.utils import require_arguments_not_none


@beartype
class BaseAggregator(ABC):
    """Base Class For Data Aggregators.

    !!! question "Where is that used?"
        Note the following are used throughout the Enrichers, e.g
        `SingleAggregatorEnricher`. This means, not to use this directly,
        but to explore when needed for advanced configuration throughout
        the enricher's primitive chosen.

    Defines the interface for aggregator implementations, which crunch stats on
    grouped data. Aggregators take `input data`, `group it` by a `column`, `apply` a `function`,
    and `yields out the results`.

    !!! note "To Implement"
        All concrete aggregators must inherit from this and
        implement `_aggregate`.

    Examples:
        >>> import urban_mapper as um
        >>> import pandas as pd
        >>> mapper = um.UrbanMapper()
        >>> data = pd.DataFrame({
        ...     "hood": ["A", "A", "B", "B"],
        ...     "value": [10, 20, 15, 25]
        ... })
        >>> enricher = mapper.enricher\
        ...     .with_data(group_by="hood", values_from="value")\
        ...     .aggregate_by(method="mean", output_column="avg_value")\
        ...     .build()
    """

    @abstractmethod
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Perform the aggregation on the input DataFrame.

        Core method for subclasses to override with specific aggregation logic.

        Args:
            input_dataframe: DataFrame to aggregate.

        Returns:
            DataFrame with at least a 'value' column of aggregated results and
            an 'indices' column of original row indices per group.
        """
        ...

    @require_arguments_not_none(
        "input_dataframe", error_msg="No input dataframe provided.", check_empty=True
    )
    def aggregate(self, input_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Aggregate the input DataFrame.

        Public method to kick off aggregation, validating input before delegating
        to `_aggregate`.

        Args:
            input_dataframe: DataFrame to aggregate. Mustn’t be None or empty.

        Returns:
            DataFrame with aggregation results.

        Raises:
            ValueError: If input_dataframe is None or empty.
        """
        return self._aggregate(input_dataframe)
