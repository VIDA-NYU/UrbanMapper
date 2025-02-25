from typing import Tuple, Any, Optional
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.modules.enricher import CreateEnricher, EnricherBase
from osmnx_mapping.utils import require_attributes_not_none


class EnricherMixin:
    def __init__(self, enricher: Optional[EnricherBase] = None):
        if enricher is not None and not isinstance(enricher, EnricherBase):
            raise TypeError(
                f"Expected EnricherBase instance, got {type(enricher).__name__}. "
                "Did you forget to call .build() on the factory?"
            )
        self.enricher = enricher

    @beartype
    def with_default(
        self,
        group_by_column: str,
        values_from_column: str,
        output_column: str = "aggregated_value",
        method: str = "mean",
        edge_method: str = "average",
    ) -> "EnricherMixin":
        self.enricher = (
            CreateEnricher()
            .with_data(group_by=group_by_column, values_from=values_from_column)
            .aggregate_with(
                method=method, edge_method=edge_method, output_column=output_column
            )
            .build()
        )
        return self

    @require_attributes_not_none(
        "enricher",
        error_msg="No enricher set. Use with_default() or pass an enricher to the constructor.",
    )
    @beartype
    def enrich_network(
        self,
        input_data: gpd.GeoDataFrame,
        input_graph: nx.MultiDiGraph,
        input_nodes: gpd.GeoDataFrame,
        input_edges: gpd.GeoDataFrame,
        **kwargs: Any,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self.enricher.enrich(
            input_data,
            input_graph,
            input_nodes,
            input_edges,
            **kwargs,
        )
