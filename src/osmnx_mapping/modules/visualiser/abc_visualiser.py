from abc import ABC, abstractmethod
from typing import Any, Union, List
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.config import DEFAULT_CRS
from osmnx_mapping.utils import require_dynamic_columns, require_arguments_not_none


class VisualiserBase(ABC):
    @beartype
    def __init__(self, coordinate_reference_system: str = DEFAULT_CRS) -> None:
        self.coordinate_reference_system = coordinate_reference_system

    @abstractmethod
    @beartype
    def _render(
        self,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        result_columns: Union[str, List[str]],
        target: str = "edges",
        **kwargs,
    ) -> Any: ...

    @require_arguments_not_none(
        "graph", error_msg="Graph cannot be None while rendering."
    )
    @require_dynamic_columns(
        "edges",
        lambda args: args["result_columns"]
        if isinstance(args["result_columns"], list)
        else [args["result_columns"]],
        condition=lambda args: args["target"] in ["edges", "both"],
    )
    @require_dynamic_columns(
        "nodes",
        lambda args: args["result_columns"]
        if isinstance(args["result_columns"], list)
        else [args["result_columns"]],
        condition=lambda args: args["target"] in ["nodes", "both"],
    )
    @beartype
    def render(
        self,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        result_columns: Union[str, List[str]],
        target: str = "edges",
        **kwargs,
    ) -> Any:
        return self._render(graph, nodes, edges, result_columns, target, **kwargs)
