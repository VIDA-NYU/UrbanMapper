from typing import Tuple, Optional
import geopandas as gpd
import networkx as nx
import osmnx as ox
from beartype import beartype
from osmnx_mapping.modules.network.abc_network import NetworkBase


@beartype
class OSMNxNetwork(NetworkBase):
    def __init__(
        self,
        place_name: Optional[str] = None,
        network_type: Optional[str] = None,
        latitude_column_name: Optional[str] = None,
        longitude_column_name: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.place_name = place_name
        self.network_type = network_type
        self.latitude_column_name = latitude_column_name
        self.longitude_column_name = longitude_column_name

    @beartype
    def build_network(
        self,
        place_name: Optional[str] = None,
        network_type: Optional[str] = None,
        render: bool = False,
    ) -> Tuple[nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        final_place_name = place_name if place_name is not None else self.place_name
        final_network_type = (
            network_type if network_type is not None else self.network_type
        )

        if final_place_name is None or final_network_type is None:
            raise ValueError(
                "Both 'place_name' and 'network_type' must be provided either at initialisation "
                "or as arguments to build_network."
            )

        self.graph = ox.graph_from_place(
            final_place_name, network_type=final_network_type
        )
        self.nodes, self.edges = ox.graph_to_gdfs(self.graph)
        if self.nodes.crs:
            self.nodes = self.nodes.to_crs(self.coordinate_reference_system)
        if self.edges.crs:
            self.edges = self.edges.to_crs(self.coordinate_reference_system)
        if render:
            ox.plot.plot_graph(self.graph, node_size=0, edge_linewidth=0.5)
        return self.graph, self.nodes, self.edges

    def _map_nearest_nodes(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_node",
        **osmnx_kwargs,
    ) -> gpd.GeoDataFrame:
        dataframe = data.copy()
        dataframe[output_column] = ox.distance.nearest_nodes(
            self.graph,
            X=dataframe[longitude_column].values,
            Y=dataframe[latitude_column].values,
            **osmnx_kwargs,
        )
        return dataframe
