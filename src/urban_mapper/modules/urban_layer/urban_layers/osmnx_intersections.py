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
    """`Urban layer` implementation for `OpenStreetMap` `street intersections`.

    This class provides methods for loading `street intersection` data from `OpenStreetMap`,
    and accessing it as `urban layers`. `Intersections` are
    represented as points (nodes in graph) where multiple street segments meet.

    The class uses `OSMnx` to retrieve `street networks` and extract their `nodes`, which
    represent intersections. It implements the `UrbanLayerBase interface`, making it
    compatible with other `UrbanMapper components`.

    !!! tip "When to use?"
        Street intersections are useful for:

        - [x] Network analysis
        - [x] Accessibility studies
        - [x] Traffic modeling
        - [x] Pedestrian safety analysis
        - [x] Urban mobility research

    Attributes:
        network: The underlying `StreetNetwork` object that provides access to the
            `OSMnx` graph data.
        layer: The `GeoDataFrame` containing the intersection points (set after loading).

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>>
        >>> # Initialise UrbanMapper
        >>> mapper = UrbanMapper()
        >>>
        >>> # Get intersections in Manhattan
        >>> intersections = mapper.urban_layer.osmnx_intersections().from_place("Manhattan, New York")
        >>>
        >>> # Visualise the intersections
        >>> intersections.static_render(node_size=5, node_color="red")
    """

    def __init__(self) -> None:
        """Initialise an empty `OSMNXIntersections` instance.

        Sets up an empty street intersections layer with default settings.
        """
        super().__init__()
        self.network: StreetNetwork | None = None

    def from_place(self, place_name: str, undirected: bool = True, **kwargs) -> None:
        """Load `street intersections` for a named place.

        This method retrieves street network data for a specified place name and
        extracts the intersections (nodes) from that network. The place name is
        geocoded to determine the appropriate area to query.

        Args:
            place_name: Name of the place to load intersections for
                (e.g., "Manhattan, New York", "Paris, France").
            undirected: Whether to consider the street network as undirected
                (default: True). When True, one-way streets are treated as
                bidirectional for the purposes of identifying intersections.
            **kwargs: Additional parameters passed to OSMnx's network retrieval
                functions. Common parameters include:

                - [x] network_type: Type of street network to retrieve ("drive",
                  "walk", "bike", etc.)
                - [x] simplify: Whether to simplify the network topology (default: True)
                - [x] retain_all: Whether to retain isolated nodes (default: False)

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).

        Returns:
            Self, for method chaining.

        Examples:
            >>> # Get walkable intersections in Brooklyn
            >>> intersections = OSMNXIntersections().from_place(
            ...     "Brooklyn, New York",
            ...     network_type="walk"
            ... )
            >>>
            >>> # Get all intersections, including isolated ones
            >>> all_intersections = OSMNXIntersections().from_place(
            ...     "Boston, MA",
            ...     retain_all=True
            ... )
        """
        self.network = StreetNetwork()
        self.network.load("place", query=place_name, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_address(self, address: str, undirected: bool = True, **kwargs) -> None:
        """Load `street intersections` for a specific address.

        This method retrieves street network data for a specified address and
        extracts the intersections (nodes) from that network. The address is geocoded
        to determine the appropriate area to query.

        Args:
            address: Address to load intersections for (e.g., "1600 Amphitheatre Parkway, Mountain View, CA").
            undirected: Whether to consider the street network as undirected
                (default: True). When True, one-way streets are treated as
                bidirectional for the purposes of identifying intersections.
            **kwargs: Additional parameters passed to OSMnx's network retrieval
                functions. Common parameters include:

                - [x] network_type: Type of street network to retrieve ("drive",
                  "walk", "bike", etc.)
                - [x] simplify: Whether to simplify the network topology (default: True)
                - [x] retain_all: Whether to retain isolated nodes (default: False)

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).

        Returns:
            Self, for method chaining.
        """
        self.network = StreetNetwork()
        self.network.load("address", address=address, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_bbox(
        self, bbox: Tuple[float, float, float, float], undirected: bool = True, **kwargs
    ) -> None:
        """Load `street intersections` for a specified bounding box.

        This method retrieves street network data for a specified bounding box
        and extracts the intersections (nodes) from that network. The bounding box
        is defined by its southwest and northeast corners.

        Args:
            bbox: Bounding box defined by southwest and northeast corners
                (e.g., (southwest_latitude, southwest_longitude, northeast_latitude, northeast_longitude)).
            undirected: Whether to consider the street network as undirected
                (default: True). When True, one-way streets are treated as
                bidirectional for the purposes of identifying intersections.
            **kwargs: Additional parameters passed to OSMnx's network retrieval
                functions. Common parameters include:

                - [x] network_type: Type of street network to retrieve ("drive",
                  "walk", "bike", etc.)
                - [x] simplify: Whether to simplify the network topology (default: True)
                - [x] retain_all: Whether to retain isolated nodes (default: False)

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).

        Returns:
            Self, for method chaining.
        """
        self.network = StreetNetwork()
        self.network.load("bbox", bbox=bbox, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_point(
        self, center_point: Tuple[float, float], undirected: bool = True, **kwargs
    ) -> None:
        """Load `street intersections` for a specified center point.

        This method retrieves street network data for a specified center point
        and extracts the intersections (nodes) from that network. The center point
        is used to determine the area to query.

        Args:
            center_point: Center point defined by its latitude and longitude
                (e.g., (latitude, longitude)).
            undirected: Whether to consider the street network as undirected
                (default: True). When True, one-way streets are treated as
                bidirectional for the purposes of identifying intersections.
            **kwargs: Additional parameters passed to OSMnx's network retrieval
                functions. Common parameters include:

                - [x] network_type: Type of street network to retrieve ("drive",
                  "walk", "bike", etc.)
                - [x] simplify: Whether to simplify the network topology (default: True)
                - [x] retain_all: Whether to retain isolated nodes (default: False)

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).

        Returns:
            Self, for method chaining.
        """
        self.network = StreetNetwork()
        self.network.load(
            "point", center_point=center_point, undirected=undirected, **kwargs
        )
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_polygon(
        self, polygon: Polygon | MultiPolygon, undirected: bool = True, **kwargs
    ) -> None:
        """Load `street intersections` for a specified polygon.

        This method retrieves street network data for a specified polygon
        and extracts the intersections (nodes) from that network. The polygon
        is used to determine the area to query.

        Args:
            polygon: Polygon or MultiPolygon defining the area of interest.
            undirected: Whether to consider the street network as undirected
                (default: True). When True, one-way streets are treated as
                bidirectional for the purposes of identifying intersections.
            **kwargs: Additional parameters passed to OSMnx's network retrieval
                functions. Common parameters include:

                - [x] network_type: Type of street network to retrieve ("drive",
                  "walk", "bike", etc.)
                - [x] simplify: Whether to simplify the network topology (default: True)
                - [x] retain_all: Whether to retain isolated nodes (default: False)

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).

        Returns:
            Self, for method chaining.
        """
        self.network = StreetNetwork()
        self.network.load("polygon", polygon=polygon, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_xml(self, filepath: str | Path, undirected: bool = True, **kwargs) -> None:
        """Load `street intersections` from a specified XML file.

        This method retrieves street network data from a specified XML file
        and extracts the intersections (nodes) from that network.

        Args:
            filepath: Path to the XML file containing street network data.
            undirected: Whether to consider the street network as undirected
                (default: True). When True, one-way streets are treated as
                bidirectional for the purposes of identifying intersections.
            **kwargs: Additional parameters passed to OSMnx's network retrieval
                functions. Common parameters include:

                - [x] network_type: Type of street network to retrieve ("drive",
                  "walk", "bike", etc.)
                - [x] simplify: Whether to simplify the network topology (default: True)
                - [x] retain_all: Whether to retain isolated nodes (default: False)

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).

        Returns:
            Self, for method chaining.
        """
        self.network = StreetNetwork()
        self.network.load("xml", filepath=filepath, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_nodes.to_crs(self.coordinate_reference_system)

    def from_file(self, file_path: str | Path, **kwargs) -> None:
        """Load `street intersections` from a specified file.

        !!! danger "Not implemented"
            This method is not implemented for `OSMNXIntersections`. It raises a
            `NotImplementedError` if called.
        """
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
        """Map points to their nearest `street intersections`.

        This internal method finds the nearest intersection (node) for each point in
        the input `GeoDataFrame` and adds a reference to that intersection as a new column.
        It's primarily used by the `UrbanLayerBase.map_nearest_layer()` method to
        implement spatial joining between point data and street intersections.

        The method uses `OSMnx's nearest_nodes` function, which efficiently identifies
        the closest node in the street network to each input point. If a threshold
        distance is specified, points beyond that distance will not be matched.

        Args:
            data: `GeoDataFrame` containing point data to map.
            longitude_column: Name of the column containing longitude values.
            latitude_column: Name of the column containing latitude values.
            output_column: Name of the column to store the indices of nearest nodes.
            threshold_distance: Maximum distance to consider a match, in the CRS units.
            _reset_layer_index: Whether to reset the index of the layer `GeoDataFrame`.
            **kwargs: Additional parameters (not used).

        Returns:
            A tuple containing:
                - The intersections `GeoDataFrame` (possibly with reset index)
                - The input `GeoDataFrame` with the new output_column added
                  (filtered if threshold_distance was specified)

        Notes:
            Unlike some other spatial joins which use GeoPandas' sjoin_nearest,
            this method uses OSMnx's optimised nearest_nodes function which
            is specifically designed for network analysis.
        """
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
        """Get the `GeoDataFrame` of the layer.

        This method returns the `GeoDataFrame` containing the loaded street intersections.

        Returns:
            gpd.GeoDataFrame: The `GeoDataFrame` containing the street intersections.
        """
        return self.layer

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_place() first."
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the layer.

        This method returns the bounding box of the loaded street intersections layer.

        Returns:
            Tuple[float, float, float, float]: The bounding box of the layer in the
                format (`minx`, `miny`, `maxx`, `maxy`).
        """
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "network", error_msg="No network loaded yet. Try from_place() first!"
    )
    def static_render(self, **plot_kwargs) -> None:
        """Render the `street intersections` on a static map.

        This method uses `OSMnx` to plot the street intersections on a static map.
        It can be used to visualise the intersections in the context of the
        surrounding street network.

        Args:
            **plot_kwargs: Additional parameters for the `OSMnx` plot function.
                Common parameters include:

                - [x] node_size: Size of the nodes (intersections) in the plot.
                - [x] node_color: Color of the nodes (intersections) in the plot.

                More can be explored in OSMnx's documentation at [https://osmnx.readthedocs.io/en/stable/](https://osmnx.readthedocs.io/en/stable/).
        """
        ox.plot_graph(self.network.graph, show=True, close=False, **plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        """Preview the `OSMNXIntersections` layer.

        This method provides a summary of the `OSMNXIntersections` layer,
        including the coordinate reference system and mappings.
        It can return the preview in either ASCII or JSON format.

        Args:
            format: The format of the preview. Can be "ascii" or "json".

                - [x] "ascii": Returns a human-readable string preview.
                - [x] "json": Returns a JSON object with the layer details.

        Returns:
            str | dict: The preview of the `OSMNXIntersections` layer in the specified format.

        Raises:
            ValueError: If the specified format is not supported.
        """
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
