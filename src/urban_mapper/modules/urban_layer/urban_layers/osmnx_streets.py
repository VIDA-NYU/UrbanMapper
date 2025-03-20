from typing import Tuple, Union, Any
import geopandas as gpd
import networkx as nx
import osmnx as ox
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
from beartype import beartype
from urban_mapper.utils import require_attributes_not_none
from ..abc_urban_layer import UrbanLayerBase


@beartype
class StreetNetwork:
    def __init__(self) -> None:
        self._graph: Union[nx.MultiDiGraph, nx.MultiGraph] | None = None

    def load(
        self, method: str, render: bool = False, undirected: bool = True, **kwargs
    ) -> None:
        method = method.lower()
        valid_methods = {"address", "bbox", "place", "point", "polygon", "xml"}
        if method not in valid_methods:
            raise ValueError(f"Invalid method. Choose from {valid_methods}")

        if method == "address":
            if "address" not in kwargs or "dist" not in kwargs:
                raise ValueError("Method 'address' requires 'address' and 'dist'")
            self._graph = ox.graph_from_address(**kwargs)
        elif method == "bbox":
            if "bbox" not in kwargs:
                raise ValueError("Method 'bbox' requires 'bbox'")
            bbox = kwargs.pop("bbox")
            if not isinstance(bbox, tuple) or len(bbox) != 4:
                raise ValueError("'bbox' must be a tuple of (left, bottom, right, top)")
            self._graph = ox.graph_from_bbox(*bbox, **kwargs)
        elif method == "place":
            if "query" not in kwargs:
                raise ValueError("Method 'place' requires 'query'")
            self._graph = ox.graph_from_place(**kwargs)
        elif method == "point":
            if "center_point" not in kwargs or "dist" not in kwargs:
                raise ValueError("Method 'point' requires 'center_point' and 'dist'")
            self._graph = ox.graph_from_point(**kwargs)
        elif method == "polygon":
            if "polygon" not in kwargs:
                raise ValueError("Method 'polygon' requires 'polygon'")
            polygon = kwargs["polygon"]
            if not isinstance(polygon, (Polygon, MultiPolygon)):
                raise ValueError("'polygon' must be a shapely Polygon or MultiPolygon")
            self._graph = ox.graph_from_polygon(**kwargs)
        elif method == "xml":
            if "filepath" not in kwargs:
                raise ValueError("Method 'xml' requires 'filepath'")
            kwargs["filepath"] = Path(kwargs["filepath"])
            self._graph = ox.graph_from_xml(**kwargs)

        if undirected:
            self._graph = ox.convert.to_undirected(self._graph)

        if render:
            ox.plot_graph(self._graph, node_size=0, edge_linewidth=0.5)

    def from_file(self, file_path: str | Path, render: bool = False) -> None:
        raise NotImplementedError(
            "Loading from file is not supported for OSMNx street and intersection networks."
        )

    @property
    def graph(self) -> Union[nx.MultiDiGraph, nx.MultiGraph]:
        if self._graph is None:
            raise ValueError("Graph not loaded. Call load() first.")
        return self._graph


@beartype
class OSMNXStreets(UrbanLayerBase):
    def __init__(self) -> None:
        super().__init__()
        self.network: StreetNetwork | None = None

    def from_place(self, place_name: str, undirected: bool = True, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("place", query=place_name, undirected=undirected, **kwargs)
        self.network._graph = ox.convert.to_undirected(self.network.graph)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_address(self, address: str, undirected: bool = True, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("address", address=address, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_bbox(
        self, bbox: Tuple[float, float, float, float], undirected: bool = True, **kwargs
    ) -> None:
        self.network = StreetNetwork()
        self.network.load("bbox", bbox=bbox, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_point(
        self, center_point: Tuple[float, float], undirected: bool = True, **kwargs
    ) -> None:
        self.network = StreetNetwork()
        self.network.load(
            "point", center_point=center_point, undirected=undirected, **kwargs
        )
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_polygon(
        self, polygon: Polygon | MultiPolygon, undirected: bool = True, **kwargs
    ) -> None:
        self.network = StreetNetwork()
        self.network.load("polygon", polygon=polygon, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_xml(self, filepath: str | Path, undirected: bool = True, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("xml", filepath=filepath, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_file(self, file_path: str | Path, **kwargs) -> None:
        raise NotImplementedError(
            "Loading from file is not supported for OSMNx street networks."
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
        output_column: str = "nearest_street",
        threshold_distance: float | None = None,
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        dataframe = data.copy()
        result = ox.distance.nearest_edges(
            self.network.graph,
            X=dataframe[longitude_column].values,
            Y=dataframe[latitude_column].values,
            return_dist=threshold_distance is not None,
        )
        if threshold_distance:
            nearest_edges, distances = result
            mask = np.array(distances) <= threshold_distance
            dataframe = dataframe[mask]
            nearest_edges = nearest_edges[mask]
        else:
            nearest_edges = result

        edge_to_idx = {k: i for i, k in enumerate(self.layer.index)}
        nearest_indices = [edge_to_idx[tuple(edge)] for edge in nearest_edges]

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
                f"Urban Layer: OSMNXStreets\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "OSMNXStreets",
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
