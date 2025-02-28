from typing import Optional, List, Union, Dict, Any


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
        return self

    def aggregate_with(
        self,
        method: str,
        edge_method: str = "average",
        output_column: str = None,
        target: str = "edges",
    ) -> "EnricherConfig":
        if not self.values_from:
            raise ValueError("Aggregation requires 'values_from'")
        if target not in ["nodes", "edges", "both"]:
            raise ValueError("target must be 'nodes', 'edges', or 'both'")
        self.action = "aggregate"
        self.aggregator_config = {"method": method}
        self.enricher_config = {
            "edge_method": edge_method,
            "output_column": output_column or f"{method}_{self.values_from[0]}",
            "target": target,
        }
        return self

    def count_by(
        self,
        edge_method: str = "sum",
        output_column: str = None,
        target: str = "edges",
    ) -> "EnricherConfig":
        if self.values_from:
            raise ValueError("Counting does not use 'values_from'")
        if target not in ["nodes", "edges", "both"]:
            raise ValueError("target must be 'nodes', 'edges', or 'both'")
        self.action = "count"
        self.aggregator_config = {}
        self.enricher_config = {
            "edge_method": edge_method,
            "output_column": output_column or "counted_value",
            "target": target,
        }
        return self

    def using_enricher(self, enricher_type: str) -> "EnricherConfig":
        self.enricher_type = enricher_type
        return self
