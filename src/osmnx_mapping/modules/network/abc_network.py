from abc import ABC, abstractmethod
from typing import Tuple, Optional
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.config import DEFAULT_CRS
from osmnx_mapping.modules.network.helpers import check_output_column
from osmnx_mapping.utils import require_attributes_not_none, require_dynamic_columns


@beartype
class NetworkBase(ABC):
    def __init__(self) -> None:
        self.graph: Optional[nx.MultiDiGraph] = None
        self.nodes: Optional[gpd.GeoDataFrame] = None
        self.edges: Optional[gpd.GeoDataFrame] = None
        self.coordinate_reference_system: str = DEFAULT_CRS

    @abstractmethod
    def build_network(
        self, place_name: str, network_type: str = "drive", render: bool = False
    ) -> Tuple[nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]: ...

    @abstractmethod
    def _map_nearest_nodes(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_node",
        **osmnx_kwargs,
    ) -> gpd.GeoDataFrame: ...

    @require_attributes_not_none(
        "graph", error_msg="Network graph not built. Please call build_network() first."
    )
    @require_dynamic_columns(
        "data", lambda args: [args["longitude_column"], args["latitude_column"]]
    )
    @check_output_column
    def map_nearest_nodes(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_node",
        reset_output_column: bool = False,
        **osmnx_kwargs,
    ) -> gpd.GeoDataFrame:
        _ = reset_output_column  # Handled by the decorators
        return self._map_nearest_nodes(
            data, longitude_column, latitude_column, output_column, **osmnx_kwargs
        )
