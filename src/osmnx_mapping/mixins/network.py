from typing import Tuple
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.modules.network.abc_network import NetworkBase
from osmnx_mapping.modules.network.networks.osmnx_network import OSMNxNetwork


@beartype
class NetworkMixin:
    def __init__(self, network_instance: NetworkBase = None) -> None:
        self.network_instance: NetworkBase = (
            network_instance if network_instance is not None else OSMNxNetwork()
        )

    @beartype
    def network_from_place(
        self, place_name: str, network_type: str = "drive", render: bool = False
    ) -> Tuple[nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self.network_instance.build_network(place_name, network_type, render)

    @beartype
    def map_nearest_street(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_node",
        reset_output_column: bool = False,
        **kwargs,
    ) -> gpd.GeoDataFrame:
        return self.network_instance.map_nearest_nodes(
            data,
            longitude_column,
            latitude_column,
            output_column,
            reset_output_column,
            **kwargs,
        )
