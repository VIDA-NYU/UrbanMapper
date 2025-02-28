from typing import Optional, Any, Union, List
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.modules.visualiser.abc_visualiser import VisualiserBase
from osmnx_mapping.modules.visualiser.visualisers.static_visualiser import (
    StaticVisualiser,
)
from osmnx_mapping.utils import require_attributes_not_none


@beartype
class VisualMixin:
    def __init__(self, visualiser: Optional[VisualiserBase] = None) -> None:
        self.visualiser_instance: VisualiserBase = (
            visualiser if visualiser is not None else StaticVisualiser()
        )

    @require_attributes_not_none(
        "visualiser_instance",
        error_msg="No visualiser instance provided. Set one in the constructor before calling this method.",
    )
    @beartype
    def visualise(
        self,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        result_columns: Union[str, List[str]],
        target: str = "edges",
        **kwargs: Any,
    ) -> Any:
        return self.visualiser_instance.render(
            graph, nodes, edges, result_columns, target, **kwargs
        )
