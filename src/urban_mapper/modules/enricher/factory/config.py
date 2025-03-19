from typing import Optional, List, Union, Dict, Any
from beartype import beartype
from urban_mapper import logger


@beartype
class EnricherConfig:
    def __init__(self):
        self.group_by: Optional[List[str]] = None
        self.values_from: Optional[List[str]] = None
        self.action: Optional[str] = None
        self.aggregator_config: Dict[str, Any] = {}
        self.enricher_type: str = "SingleAggregatorEnricher"
        self.enricher_config: Dict[str, Any] = {}

    def with_data(
        self,
        group_by: Union[str, List[str]],
        values_from: Optional[Union[str, List[str]]] = None,
    ) -> "EnricherConfig":
        self.group_by = [group_by] if isinstance(group_by, str) else group_by
        self.values_from = (
            [values_from] if isinstance(values_from, str) else values_from
        )
        logger.log(
            "DEBUG_LOW",
            f"WITH_DATA: Initialised EnricherConfig with "
            f"group_by={self.group_by} and values_from={self.values_from}",
        )
        return self

    def aggregate_by(self, method: str, output_column: str = None) -> "EnricherConfig":
        if not self.values_from:
            raise ValueError("Aggregation requires 'values_from'")
        self.action = "aggregate"
        self.aggregator_config = {"method": method}
        self.enricher_config = {
            "output_column": output_column or f"{method}_{self.values_from[0]}"
        }
        logger.log(
            "DEBUG_LOW",
            f"AGGREGATE_BY: Initialised EnricherConfig with "
            f"method={method} and output_column={output_column}",
        )
        return self

    def count_by(self, output_column: str = None) -> "EnricherConfig":
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
        self.enricher_type = primitive_type
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised EnricherConfig with primitive_type={primitive_type}",
        )
        return self
