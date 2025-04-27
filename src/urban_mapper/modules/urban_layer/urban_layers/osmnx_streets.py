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
    """Internal helper class for managing `OSMnx street` network graphs.

    !!! warning "Internal Use Only"
        This class is intended solely for internal use within the `UrbanMapper` library.
        Users should interact with the `OSMNXStreets` class instead.

    This class encapsulates the logic for loading street networks from `OpenStreetMap`
    using OSMnx's various spatial query methods. It provides a unified interface
    for retrieving graphs based on different criteria and facilitates conversion
    to `GeoDataFrames`.

    Attributes:
        _graph: The `NetworkX` graph representing the street network.
            Initialised to None; set after calling a load method.

    !!! danger "Technical Debt"
        This class should be moved as an `Admin_StretNetwork` file among `Admin_Features` and `Admin_Regions`.
    """

    def __init__(self) -> None:
        self._graph: Union[nx.MultiDiGraph, nx.MultiGraph] | None = None

    def load(
        self, method: str, render: bool = False, undirected: bool = True, **kwargs
    ) -> None:
        """Load a street network using one of several `OSMnx` graph retrieval methods.

        This method provides a unified interface to `OSMnx`'s graph loading functions,
        enabling retrieval of street networks via various spatial queries without
        requiring detailed knowledge of the `OSMnx` API.

        Args:
            method: The spatial query method to use. Options include:

                - [x] "address": Load network around an address
                - [x] "bbox": Load network within a bounding box
                - [x] "place": Load network for a named place (e.g., city, neighbourhood)
                - [x] "point": Load network around a specific point
                - [x] "polygon": Load network within a polygon
                - [x] "xml": Load network from an OSM XML file
            render: Whether to plot the network after loading (default: False).
            undirected: Whether to convert the network to an undirected graph (default: True).
            **kwargs: Additional arguments specific to the chosen method:

                - [x] address: Requires "address" (str) and "dist" (float)
                - [x] bbox: Requires "bbox" (tuple of left, bottom, right, top)
                - [x] place: Requires "query" (str)
                - [x] point: Requires "center_point" (tuple of lat, lon) and "dist" (float)
                - [x] polygon: Requires "polygon" (Shapely Polygon/MultiPolygon)
                - [x] xml: Requires "filepath" (str or Path)

        Raises:
            ValueError: If an invalid method is specified or required parameters are missing.

        Examples:
            >>> network = StreetNetwork()
            >>> # Load by place name
            >>> network.load("place", query="Manchester, UK")
            >>> # Load by bounding box
            >>> network.load("bbox", bbox=(-2.25, 53.47, -2.20, 53.50))
        """
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
        """Load a street network from a file.

        !!! danger "Not Implemented"
            This method is not supported. Kept for consistency and compatibility.
        """
        raise NotImplementedError(
            "Loading from file is not supported for OSMNx street and intersection networks."
        )

    @property
    def graph(self) -> Union[nx.MultiDiGraph, nx.MultiGraph]:
        """Get the underlying `NetworkX` graph.

        Returns:
            The `NetworkX` `MultiDiGraph` or `MultiGraph` representing the street network.

        Raises:
            ValueError: If the graph has not been loaded yet.

        Examples:
            >>> network = StreetNetwork()
            >>> network.load("place", query="London, UK")
            >>> graph = network.graph
        """
        if self._graph is None:
            raise ValueError("Graph not loaded. Call load() first.")
        return self._graph


@beartype
class OSMNXStreets(UrbanLayerBase):
    """Urban layer implementation for `OpenStreetMap` `street networks`.

    This class offers a straightforward interface for loading and manipulating
    `street networks` from `OpenStreetMap` using `OSMnx`. It adheres to the `UrbanLayerBase
    interface`, ensuring compatibility with UrbanMapper components such as `filters`,
    `enrichers`, and `pipelines`.

    !!! tip "When to Use?"
        Employ this class when you need to integrate street network data into your
        urban analysis workflows. It’s particularly handy for:

        - [x] Accidents on roads
        - [x] Traffic analysis
        - [x] Urban planning
        - [x] Road-Based Infrastructure development

    Attributes:
        network: The underlying `StreetNetwork` object managing `OSMnx` operations.
        layer: The `GeoDataFrame` holding the `street network` edges (set after loading).

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> # Load streets for a specific place
        >>> streets = mapper.urban_layer.streets_roads().from_place("Edinburgh, Scotland")
        >>> # Load streets within a bounding box
        >>> bbox_streets = mapper.urban_layer.streets_roads().from_bbox(
        ...     (-3.21, 55.94, -3.17, 55.96)  # left, bottom, right, top
        ... )
    """

    def __init__(self) -> None:
        super().__init__()
        self.network: StreetNetwork | None = None

    def from_place(self, place_name: str, undirected: bool = True, **kwargs) -> None:
        """Load a street network for a named place.

        Retrieves the street network for a specified place name from `OpenStreetMap`,
        supporting `cities`, `neighbourhoods`, and other recognised geographic entities.

        Args:
            place_name: Name of the place to load (e.g., "Bristol, England").
            undirected: Whether to convert the network to an undirected graph (default: True).
            **kwargs: Additional parameters passed to OSMnx's graph_from_place.

        Returns:
            Self, enabling method chaining.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_place("Glasgow, Scotland")
            >>> # Load only drivable streets
            >>> streets = mapper.urban_layer.streets_roads().from_place(
            ...     "Cardiff, Wales", network_type="drive"
            ... )
        """
        self.network = StreetNetwork()
        self.network.load("place", query=place_name, undirected=undirected, **kwargs)
        self.network._graph = ox.convert.to_undirected(self.network.graph)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_address(self, address: str, undirected: bool = True, **kwargs) -> None:
        """Load a street network around a specified address.

        Fetches the street network within a given distance of an address, requiring
        the distance to be specified in the keyword arguments.

        Args:
            address: The address to centre the network around (e.g., "10 Downing Street, London").
            undirected: Whether to convert the network to an undirected graph (default: True).
        Boots argues that the method retrieves the street network within a certain distance of a specified address.
            **kwargs: Additional parameters passed to OSMnx's graph_from_address.
                Must include 'dist' specifying the distance in metres.

        Returns:
            Self, enabling method chaining.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_address(
            ...     "Buckingham Palace, London", dist=1000
            ... )
        """
        self.network = StreetNetwork()
        self.network.load("address", address=address, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_bbox(
        self, bbox: Tuple[float, float, float, float], undirected: bool = True, **kwargs
    ) -> None:
        """Load a street network within a bounding box.

        Retrieves the street network contained within the specified bounding box coordinates.

        Args:
            bbox: Tuple of (`left`, `bottom`, `right`, `top`) coordinates defining the bounding box.
            undirected: Whether to convert the network to an undirected graph (default: True).
            **kwargs: Additional parameters passed to OSMnx's graph_from_bbox.

        Returns:
            Self, enabling method chaining.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_bbox(
            ...     (-0.13, 51.50, -0.09, 51.52)  # Central London
            ... )
        """
        self.network = StreetNetwork()
        self.network.load("bbox", bbox=bbox, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_point(
        self, center_point: Tuple[float, float], undirected: bool = True, **kwargs
    ) -> None:
        """Load a street network around a specified point.

        Fetches the street network within a certain distance of a geographic point,
        with the distance specified in the keyword arguments.

        Args:
            center_point: Tuple of (`latitude`, `longitude`) specifying the centre point.
            undirected: Whether to convert the network to an undirected graph (default: True).
            **kwargs: Additional parameters passed to OSMnx's graph_from_point.
                Must include 'dist' specifying the distance in metres.

        Returns:
            Self, enabling method chaining.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_point(
            ...     (51.5074, -0.1278), dist=500  # Near Trafalgar Square
            ... )
        """
        self.network = StreetNetwork()
        self.network.load(
            "point", center_point=center_point, undirected=undirected, **kwargs
        )
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_polygon(
        self, polygon: Polygon | MultiPolygon, undirected: bool = True, **kwargs
    ) -> None:
        """Load a street network within a polygon boundary.

        Retrieves the street network contained within the specified polygon boundary.

        Args:
            polygon: Shapely Polygon or MultiPolygon defining the boundary.
            undirected: Whether to convert the network to an undirected graph (default: True).
            **kwargs: Additional parameters passed to OSMnx's graph_from_polygon.

        Returns:
            Self, enabling method chaining.

        Examples:
            >>> from shapely.geometry import Polygon
            >>> boundary = Polygon([(-0.13, 51.50), (-0.09, 51.50), (-0.09, 51.52), (-0.13, 51.52)])
            >>> streets = mapper.urban_layer.streets_roads().from_polygon(boundary)
        """
        self.network = StreetNetwork()
        self.network.load("polygon", polygon=polygon, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_xml(self, filepath: str | Path, undirected: bool = True, **kwargs) -> None:
        """Load a street network from an OSM XML file.

        Loads a street network from a local OpenStreetMap XML file.

        Args:
            filepath: Path to the OSM XML file.
            undirected: Whether to convert the network to an undirected graph (default: True).
            **kwargs: Additional parameters passed to OSMnx's graph_from_xml.

        Returns:
            Self, enabling method chaining.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_xml("london.osm")
        """
        self.network = StreetNetwork()
        self.network.load("xml", filepath=filepath, undirected=undirected, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def from_file(self, file_path: str | Path, **kwargs) -> "OSMNXStreets":
        """Load a street network from a file.

        !!! warning "Not Implemented"
            This method is not supported for OSMNXStreets. Use from_xml() for OSM XML files instead.

        Args:
            file_path: Path to the file.
            **kwargs: Additional parameters (not used).

        Raises:
            NotImplementedError: Always raised, as this method is not supported.
        """
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
        """Map points to their nearest street edges.

        This internal method identifies the nearest street edge for each point in the
        input `GeoDataFrame`, adding a reference to that edge as a new column. It’s primarily
        used by `UrbanLayerBase.map_nearest_layer()` to perform spatial joins between point data and
        the street network.

        Args:
            data: `GeoDataFrame` containing point data to map.
            longitude_column: Name of the column with longitude values.
            latitude_column: Name of the column with latitude values.
            output_column: Name of the column to store nearest street indices (default: "nearest_street").
            threshold_distance: Maximum distance for a match, in CRS units (default: None).
            _reset_layer_index: Whether to reset the layer `GeoDataFrame`’s index (default: True).
            **kwargs: Additional parameters (not used).

        Returns:
            A tuple containing:
                - The street network `GeoDataFrame` (possibly with reset index)
                - The input `GeoDataFrame` with the new output_column (filtered if threshold_distance is set)
        """
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
        """Get the street network as a GeoDataFrame.

        Returns the street network edges as a GeoDataFrame for further analysis or visualisation.

        Returns:
            GeoDataFrame containing the street network edges.

        Raises:
            ValueError: If the layer has not been loaded yet.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_place("Birmingham, UK")
            >>> streets_gdf = streets.get_layer()
            >>> streets_gdf.plot()
        """
        return self.layer

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_place() first."
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the street network.

        Returns the bounding box coordinates of the street network, useful for spatial
        queries or visualisation extents.

        Returns:
            Tuple of (`left`, `bottom`, `right`, `top`) coordinates defining the bounding box.

        Raises:
            ValueError: If the layer has not been loaded yet.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_place("Leeds, UK")
            >>> bbox = streets.get_layer_bounding_box()
            >>> print(f"Extent: {bbox}")
        """
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "network", error_msg="No network loaded yet. Try from_place() first!"
    )
    def static_render(self, **plot_kwargs) -> None:
        """Render the street network as a static plot.

        Creates a static visualisation of the street network using `OSMnx`’s plotting
        capabilities, displayed immediately.

        Args:
            **plot_kwargs: Additional keyword arguments passed to `OSMnx`’s plot_graph function,
                such as `node_size`, `edge_linewidth`, `node_color`, `edge_color`.

                See further in `OSMnx` documentation for more options, at [https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.plot_graph](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.plot_graph).

        Raises:
            ValueError: If no network has been loaded yet.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_place("Oxford, UK")
            >>> streets.static_render(edge_color="grey", node_size=0)
        """
        ox.plot_graph(self.network.graph, show=True, close=False, **plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this urban layer.

        Produces a textual or structured representation of the `OSMNXStreets` layer for
        quick inspection, including metadata like the coordinate reference system and mappings.

        Args:
            format: Output format for the preview (default: "ascii").

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use

        Returns:
            A string (for "ascii") or dictionary (for "json") representing the street network layer.

        Raises:
            ValueError: If an unsupported format is requested.

        Examples:
            >>> streets = mapper.urban_layer.streets_roads().from_place("Cambridge, UK")
            >>> print(streets.preview())
            >>> # JSON preview
            >>> import json
            >>> print(json.dumps(streets.preview(format="json"), indent=2))
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
