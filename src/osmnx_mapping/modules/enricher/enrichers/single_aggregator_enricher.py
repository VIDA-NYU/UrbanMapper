from typing import Tuple, Callable, Any, Optional
import geopandas as gpd
import networkx as nx
import pandas as pd
from beartype import beartype
import osmnx
from osmnx_mapping.modules.enricher.abc_enricher import EnricherBase
from osmnx_mapping.modules.enricher.aggregator.abc_aggregator import BaseAggregator
from osmnx_mapping.modules.enricher.factory import EnricherConfig
from osmnx_mapping.modules.enricher.factory.preview import PreviewBuilder
from osmnx_mapping.modules.enricher.factory.registries import ENRICHER_REGISTRY


class SingleAggregatorEnricher(EnricherBase):
    @beartype
    def __init__(
        self,
        aggregator: BaseAggregator,
        output_column: str = "street_count",
        edge_method: str | Callable[[pd.Series, pd.Series], float] = "average",
        target: str = "edges",
        config: Optional[EnricherConfig] = None,
    ) -> None:
        super().__init__(config)
        self.aggregator = aggregator
        self.output_column = output_column
        self.target = target
        self.config = config or EnricherConfig()
        self._set_edge_method(edge_method)

    def _set_edge_method(
        self, method: str | Callable[[pd.Series, pd.Series], float]
    ) -> None:
        if callable(method):
            self.edge_method = method
        elif isinstance(method, str):
            if method not in self.EDGE_METHODS:
                raise ValueError(
                    f"Unknown edge method '{method}'. Available: {list(self.EDGE_METHODS.keys())}"
                )
            self.edge_method = self.EDGE_METHODS[method]
        else:
            raise TypeError("edge_method must be a string or callable")

    @beartype
    def _enrich(
        self,
        data: gpd.GeoDataFrame,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        **kwargs: Any,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        updated_nodes, updated_edges = osmnx.graph_to_gdfs(graph)
        updated_edges = updated_edges.reset_index()
        updated_edges = self.reproject_edges(updated_edges, edges.crs.to_string())

        aggregated_series = self.aggregator.aggregate(data)

        if self.target in ["nodes", "both"]:
            updated_nodes[self.output_column] = updated_nodes.index.map(
                aggregated_series
            ).fillna(0)

        if self.target in ["edges", "both"]:
            updated_edges[self.output_column] = updated_edges.apply(
                lambda row: self.edge_method(row, aggregated_series), axis=1
            ).fillna(0)

        updated_edges = self.ensure_multiindex(updated_edges)
        updated_graph = osmnx.graph_from_gdfs(updated_nodes, updated_edges)
        return data, updated_graph, updated_nodes, updated_edges

    @beartype
    def preview(self, format: str = "ascii") -> str:
        preview_builder = PreviewBuilder(self.config, ENRICHER_REGISTRY)
        return preview_builder.build_preview(format=format)
