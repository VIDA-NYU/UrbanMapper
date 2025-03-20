from typing import Tuple, Any
import geopandas as gpd
import osmnx as ox
from beartype import beartype
from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon
import numpy as np

from urban_mapper.utils import require_attributes_not_none
from .osmnx_streets import StreetNetwork
from ..abc_urban_layer import UrbanLayerBase


@beartype
class OSMNXIntersections(UrbanLayerBase):
    def __init__(self) -> None:
        super().__init__()
        self.network: StreetNetwork | None = None

    def from_place(self, place_name: str, undirected: bool = True, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("place", query=place_name, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_address(self, address: str, undirected: bool = True, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("address", address=address, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_bbox(
        self, bbox: Tuple[float, float, float, float], undirected: bool = True, **kwargs
    ) -> None:
        self.network = StreetNetwork()
        self.network.load("bbox", bbox=bbox, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_point(
        self, center_point: Tuple[float, float], undirected: bool = True, **kwargs
    ) -> None:
        self.network = StreetNetwork()
        self.network.load(
            "point", center_point=center_point, undirected=undirected, **kwargs
        )
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_polygon(
        self, polygon: Polygon | MultiPolygon, undirected: bool = True, **kwargs
    ) -> None:
        self.network = StreetNetwork()
        self.network.load("polygon", polygon=polygon, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_xml(self, filepath: str | Path, undirected: bool = True, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("xml", filepath=filepath, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_file(self, file_path: str | Path, **kwargs) -> None:
        raise NotImplementedError(
            "Loading from file is not supported for OSMNx intersection networks."
        )

    @require_attributes_not_none(
        "network",
        error_msg="Network not loaded. Call from_place() or other load methods first.",
    )
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_node_idx",
        threshold_distance: float | None = None,
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        dataframe = data.copy()
        result = ox.distance.nearest_nodes(
            self.network.graph,
            X=dataframe[longitude_column].values,
            Y=dataframe[latitude_column].values,
            return_dist=threshold_distance is not None,
        )
        if threshold_distance:
            nearest_nodes, distances = result
            mask = np.array(distances) <= threshold_distance
            dataframe = dataframe[mask]
            nearest_nodes = nearest_nodes[mask]
        else:
            nearest_nodes = result

        edge_to_idx = {k: i for i, k in enumerate(self.layer.index)}
        nearest_indices = [edge_to_idx[edge] for edge in nearest_nodes]

        dataframe[output_column] = nearest_indices
        if _reset_layer_index:
            self.layer = self.layer.reset_index()
        return self.layer, dataframe

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_place() first."
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        return self.layer

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_place() first."
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "network", error_msg="No network loaded yet. Try from_place() first!"
    )
    def static_render(self, **plot_kwargs) -> None:
        ox.plot_graph(self.network.graph, show=True, close=False, **plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        mappings_str = (
            "\n".join(
                "Mapping:\n"
                f"    - lon={m.get('longitude_column', 'N/A')}, "
                f"lat={m.get('latitude_column', 'N/A')}, "
                f"output={m.get('output_column', 'N/A')}"
                for m in self.mappings
            )
            if self.mappings
            else "    No mappings"
        )
        if format == "ascii":
            return (
                f"Urban Layer: OSMNXIntersections\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "OSMNXIntersections",
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
