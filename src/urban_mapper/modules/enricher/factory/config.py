from typing import Optional, List, Union, Dict, Any, Callable
from beartype import beartype
from urban_mapper import logger


@beartype
class EnricherConfig:
    """Configuration Class For `Enrichers`.

    Offers a fluent chaining-based methods interface to configure enrichers—how data is `grouped`,
    values `aggregated`, `methods applied`, and `outputs named`.

    Attributes:
        group_by: Columns to group by during enrichment.
        values_from: Columns to extract values from for aggregation.
        action: Action type (e.g., "aggregate", "count").
        aggregator_config: Params for the aggregator.
        enricher_type: Type of enricher to use.
        enricher_config: Params for the enricher.
        debug: Whether to include debug info.
        data_id: ID of the dataset to be transformed

    Examples:
        >>> import urban_mapper as um
        >>> mapper = um.UrbanMapper()
        >>> config = mapper.enricher\
        ...     .with_data(group_by="street")\
        ...     .count_by(output_column="trips")
    """

    def __init__(self):
        self.group_by: Optional[List[str]] = None
        self.values_from: Optional[List[str]] = None
        self.action: Optional[str] = None
        self.aggregator_config: Dict[str, Any] = {}
        self.enricher_type: str = "SingleAggregatorEnricher"
        self.enricher_config: Dict[str, Any] = {}
        self.debug: bool = False
        self.data_id: Optional[str] = None

    def with_data(
        self,
        group_by: Union[str, List[str]],
        values_from: Optional[Union[str, List[str]]] = None,
        data_id: Optional[str] = None,
    ) -> "EnricherConfig":
        """Set columns for grouping and value extraction.

        Configures grouping columns and optional value columns for aggregation.

        !!! note "Read the following like"
            ``With data, grouping by <group_by> and extracting values from <values_from>.''

            Follow the other ``Read the following like`` notes for the continuity of the
            examples.

        Args:
            group_by: Column(s) to group by—string or list.
            values_from: Column(s) to aggregate—string or list, optional.
            data_id: ID of the dataset to be transformed

        Returns:
            Self, for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> config = mapper.enricher.with_data(group_by="street")
        """
        self.group_by = [group_by] if isinstance(group_by, str) else group_by
        self.values_from = (
            [values_from] if isinstance(values_from, str) else values_from
        )
        self.data_id = data_id
        logger.log(
            "DEBUG_LOW",
            f"WITH_DATA: Initialised EnricherConfig with "
            f"group_by={self.group_by} and values_from={self.values_from}",
        )
        return self

    def aggregate_by(
        self, method: Union[str, Callable], output_column: str = None
    ) -> "EnricherConfig":
        """Set up aggregation with a method.

        Configures aggregation of `values_from` using the given method.

        !!! note "Read the following like"
            ``Aggregate by <method> with the output being a new column with the name: <output_column>.''

            Follow the other ``Read the following like`` notes for the continuity of the
            examples.

        Args:
            method: Aggregation method—string (e.g., "mean") or callable.
            output_column: Name for aggregated values (optional).

        Returns:
            Self, for chaining.

        Raises:
            ValueError: If `values_from` isn’t set.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> config = mapper.enricher\
            ...     .with_data(group_by="street", values_from="fare")\
            ...     .aggregate_by("mean", "avg_fare")
        """
        if not self.values_from:
            raise ValueError("Aggregation requires 'values_from'")
        self.action = "aggregate"
        self.aggregator_config = {"method": method}
        if output_column:
            self.enricher_config["output_column"] = output_column
        else:
            method_name = method if isinstance(method, str) else "custom"
            self.enricher_config["output_column"] = (
                f"{method_name}_{self.values_from[0]}"
            )
        return self

    def count_by(self, output_column: str = None) -> "EnricherConfig":
        """Set up counting per group.

        Configures counting of occurrences per `group_by` column.

        !!! note "Read the following like"
            ``Count by <group_by> with the output being a new column with the name: <output_column>.''

            Follow the other ``Read the following like`` notes for the continuity of the
            examples.

        Args:
            output_column: Name for count values (default: "counted_value").

        Returns:
            Self, for chaining.

        Raises:
            ValueError: If `values_from` is set (not needed for counting).

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> config = mapper.enricher\
            ...     .with_data(group_by="street")\
            ...     .count_by("trip_count")
        """
        if self.values_from:
            raise ValueError("Counting does not use 'values_from'")
        self.action = "count"
        self.aggregator_config = {}
        self.enricher_config = {"output_column": output_column or "counted_value"}
        logger.log(
            "DEBUG_LOW",
            f"COUNT_BY: Initialised EnricherConfig with output_column={output_column}",
        )
        return self

    def with_type(self, primitive_type: str) -> "EnricherConfig":
        """Set the enricher type.

        Specifies the enricher type for the configuration.

        !!! note "Read the following like"
            ``With the following enricher's type: <primitive_type>.''

            Follow the other ``Read the following like`` notes for the continuity of the
            examples.

        !!! tip "For The Time Being, Only One Enricher Type Is Supported"

            ``SingleAggregatorEnricher`` is the only supported enricher type for now.
            You have therefore no need to specify the type of enricher you want to use.
            It'll become deprecated in the future, if more enricher types primitives are
            implemented.

        Args:
            primitive_type: Enricher type name (e.g., "SingleAggregatorEnricher").

        Returns:
            Self, for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> config = mapper.enricher\
            ...     .with_data(group_by="street")\
            ...     .count_by()\
            ...     .with_type("SingleAggregatorEnricher")
        """
        self.enricher_type = primitive_type
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised EnricherConfig with primitive_type={primitive_type}",
        )
        return self
