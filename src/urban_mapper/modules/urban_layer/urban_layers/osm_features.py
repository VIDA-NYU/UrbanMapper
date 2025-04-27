from typing import Tuple, Dict, Any
import geopandas as gpd
from pathlib import Path
from beartype import beartype

from urban_mapper.utils import require_attributes_not_none

from .admin_features_ import AdminFeatures
from ..abc_urban_layer import UrbanLayerBase

from shapely.geometry import Polygon, MultiPolygon


@beartype
class OSMFeatures(UrbanLayerBase):
    """`Urban layer` implementation for arbitrary `OpenStreetMap features`.

    This class provides methods for loading various types of `OpenStreetMap features`
    into `UrbanMapper`, based on user-specified `tags`. It handles the details of
    querying `OSM data` using different spatial contexts (`place names`, `addresses`,
    `bounding boxes`, etc.) and converting the results to `GeoDataFrames`.

    The class is designed to be both usable directly and subclassed for more
    specific feature types. It implements the `UrbanLayerBase interface`, making
    it compatible with other `UrbanMapper` components.

    !!! tip "When to use?"
        OSM Features are useful for:

        - [x] Looking to do analysis on specific features in `OpenStreetMap`.
        - [x] Wanting to load features based on `tags` (e.g., `amenity`, `building`, etc.).

    Attributes:
        feature_network: The underlying `AdminFeatures` object used to fetch OSM data.
        tags: Dictionary of OpenStreetMap `tags` used to filter features.
        layer: The `GeoDataFrame` containing the loaded OSM features (set after loading).

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>>
        >>> # Load all restaurants in Manhattan
        >>> restaurants = mapper.urban_layer.osm_features().from_place(
        ...     "Manhattan, New York",
        ...     tags={"amenity": "restaurant"}
        ... )
        >>>
        >>> # Load parks within a bounding box
        >>> parks = mapper.urban_layer.osm_features().from_bbox(
        ...     (-74.01, 40.70, -73.97, 40.75),  # NYC area
        ...     tags={"leisure": "park"}
        ... )
    """

    def __init__(self) -> None:
        super().__init__()
        self.feature_network: AdminFeatures | None = None
        self.tags: Dict[str, str] | None = None

    def from_place(
        self, place_name: str, tags: Dict[str, str | bool | dict | list], **kwargs
    ) -> None:
        """Load `OpenStreetMap features` for a named place.

        This method retrieves OSM features matching the specified tags for a
        given place name. The place name is geocoded to determine the appropriate
        area to query.

        Args:
            place_name: Name of the place to query (e.g., `Manhattan, New York`).
            tags: Dictionary of OSM tags to filter features. Examples:

                - [x] {"amenity": "restaurant"} - All restaurants
                - [x] {"building": True} - All buildings
                - [x] {"leisure": ["park", "garden"]} - Parks and gardens
                - [x] {"natural": "water"} - Water bodies

                See more in the OSM documentation, [here](https://wiki.openstreetmap.org/wiki/Map_Features)
                as well as in the `OSMnx` documentation, [here](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.features_from_place).
            **kwargs: Additional parameters passed to OSMnx's features_from_place.

        Returns:
            Self, for method chaining.

        Examples:
            >>> # Load all hospitals in Chicago
            >>> hospitals = OSMFeatures().from_place(
            ...     "Chicago, Illinois",
            ...     tags={"amenity": "hospital"}
            ... )
            >>>
            >>> # Load multiple amenity types with a list
            >>> poi = OSMFeatures().from_place(
            ...     "Paris, France",
            ...     tags={"tourism": ["hotel", "museum", "attraction"]}
            ... )
        """
        self.tags = tags
        self.feature_network = AdminFeatures()
        self.feature_network.load("place", tags, query=place_name, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_address(
        self,
        address: str,
        tags: Dict[str, str | bool | dict | list],
        dist: float,
        **kwargs,
    ) -> None:
        """Load `OpenStreetMap features` for a specific address.

        This method retrieves `OSM` features matching the specified tags for a
        given address. The address is geocoded to determine the appropriate
        area to query.

        Args:
            address: Address to query (e.g., `1600 Amphitheatre Parkway, Mountain View, CA`).
            tags: Dictionary of OSM tags to filter features. Examples:

                - [x] {"amenity": "restaurant"} - All restaurants
                - [x] {"building": True} - All buildings
                - [x] {"leisure": ["park", "garden"]} - Parks and gardens
                - [x] {"natural": "water"} - Water bodies

                See more in the OSM documentation, [here](https://wiki.openstreetmap.org/wiki/Map_Features)
                as well as in the `OSMnx` documentation, [here](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.features_from_address).

            dist: Distance in meters to search around the address.
            **kwargs: Additional parameters passed to OSMnx's features_from_address.

        Returns:
            Self, for method chaining.

        Examples:
            >>> # Load all restaurants within 500 meters of a specific address
            >>> restaurants = OSMFeatures().from_address(
            ...     "1600 Amphitheatre Parkway, Mountain View, CA",
            ...     tags={"amenity": "restaurant"},
            ...     dist=500
            ... )
            >>>
            # Load all parks within 1 km of a specific address
            >>> parks = OSMFeatures().from_address(
            ...     "Central Park, New York, NY",
            ...     tags={"leisure": "park"},
            ...     dist=1000
            ... )
        """

        self.tags = tags
        self.feature_network = AdminFeatures()
        self.feature_network.load("address", tags, address=address, dist=dist, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_bbox(
        self,
        bbox: Tuple[float, float, float, float],
        tags: Dict[str, str | bool | dict | list],
        **kwargs,
    ) -> None:
        """Load `OpenStreetMap features` for a specific bounding box.

        This method retrieves OSM features matching the specified tags for a
        given bounding box. The bounding box is defined by its coordinates.

        Args:
            bbox: Bounding box coordinates in the format (min_lon, min_lat, max_lon, max_lat).
            tags: Dictionary of OSM tags to filter features. Examples:

                - [x] {"amenity": "restaurant"} - All restaurants
                - [x] {"building": True} - All buildings
                - [x] {"leisure": ["park", "garden"]} - Parks and gardens
                - [x] {"natural": "water"} - Water bodies

                See more in the OSM documentation, [here](https://wiki.openstreetmap.org/wiki/Map_Features)
                as well as in the `OSMnx` documentation, [here](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.features_from_bbox).

            **kwargs: Additional parameters passed to OSMnx's features_from_bbox.

        Returns:
            Self, for method chaining.

        Examples:
            >>> # Load all schools within a bounding box in San Francisco
            >>> schools = OSMFeatures().from_bbox(
            ...     (-122.45, 37.75, -122.40, 37.80),
            ...     tags={"amenity": "school"}
            ... )
        """
        self.tags = tags
        self.feature_network = AdminFeatures()
        self.feature_network.load("bbox", tags, bbox=bbox, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_point(
        self,
        center_point: Tuple[float, float],
        tags: Dict[str, str | bool | dict | list],
        dist: float,
        **kwargs,
    ) -> None:
        """Load `OpenStreetMap features` for a specific point.

        This method retrieves OSM features matching the specified tags for a
        given point. The point is defined by its coordinates.

        Args:
            center_point: Coordinates of the point in the format (longitude, latitude).
            tags: Dictionary of OSM tags to filter features. Examples:

                - [x] {"amenity": "restaurant"} - All restaurants
                - [x] {"building": True} - All buildings
                - [x] {"leisure": ["park", "garden"]} - Parks and gardens
                - [x] {"natural": "water"} - Water bodies

                See more in the OSM documentation, [here](https://wiki.openstreetmap.org/wiki/Map_Features)
                as well as in the `OSMnx` documentation, [here](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.features_from_point).

            dist: Distance in meters to search around the point.
            **kwargs: Additional parameters passed to OSMnx's features_from_point.

        Returns:
            Self, for method chaining.

        Examples:
            >>> # Load all restaurants within 500 meters of a specific point
            >>> restaurants = OSMFeatures().from_point(
            ...     (37.7749, -122.4194),  # San Francisco coordinates
            ...     tags={"amenity": "restaurant"},
            ...     dist=500
            ... )
        """
        self.tags = tags
        self.feature_network = AdminFeatures()
        self.feature_network.load(
            "point", tags, center_point=center_point, dist=dist, **kwargs
        )
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_polygon(
        self,
        polygon: Polygon | MultiPolygon,
        tags: Dict[str, str | bool | dict | list],
        **kwargs,
    ) -> None:
        """Load `OpenStreetMap features` for a specific polygon.

        This method retrieves OSM features matching the specified tags for a
        given polygon. The polygon is defined by its geometry.

        Args:
            polygon: Shapely Polygon or MultiPolygon object defining the area.
            tags: Dictionary of OSM tags to filter features. Examples:

                - [x] {"amenity": "restaurant"} - All restaurants
                - [x] {"building": True} - All buildings
                - [x] {"leisure": ["park", "garden"]} - Parks and gardens
                - [x] {"natural": "water"} - Water bodies

                See more in the OSM documentation, [here](https://wiki.openstreetmap.org/wiki/Map_Features)
                as well as in the `OSMnx` documentation, [here](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.features_from_polygon).

            **kwargs: Additional parameters passed to OSMnx's features_from_polygon.

        Returns:
            Self, for method chaining.

        Examples:
            >>> # Load all parks within a specific polygon
            >>> parks = OSMFeatures().from_polygon(
            ...     Polygon([(37.7749, -122.4194), (37.7849, -122.4294), (37.7949, -122.4194)]),
            ...     # 👆Can get polygon from geocoding an address/place via GeoPY.
            ...     tags={"leisure": "park"}
            ... )
        """
        self.tags = tags
        self.feature_network = AdminFeatures()
        self.feature_network.load("polygon", tags, polygon=polygon, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_file(self, file_path: str | Path, **kwargs) -> None:
        """Load `OpenStreetMap features` from a file.

        !!! danger "Not Implemented"
            This method is not implemented yet. It raises a `NotImplementedError`.
            You can use the other loading methods (e.g., `from_place`, `from_bbox`)
            to load OSM features.
        """
        raise NotImplementedError("Loading OSM features from file is not supported.")

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call a loading method (e.g., from_place) first.",
    )
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_feature",
        threshold_distance: float | None = None,
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """Map points to their nearest `OSM features`.

        This internal method finds the nearest OSM feature for each point in
        the input `GeoDataFrame` and adds a reference to that feature as a new column.
        It's primarily used by the `UrbanLayerBase.map_nearest_layer()` method to
        implement spatial joining between your dataset point data and OSM features compoents.

        The method handles both points with explicit geometry and points defined
        by longitude/latitude columns. It also automatically converts coordinate
        systems to ensure accurate distance calculations.

        Args:
            data: `GeoDataFrame` containing point data to map.
            longitude_column: Name of the column containing longitude values.
            latitude_column: Name of the column containing latitude values.
            output_column: Name of the column to store the indices of nearest features.
            threshold_distance: Maximum distance to consider a match, in the CRS units.
            _reset_layer_index: Whether to reset the index of the layer GeoDataFrame.
            **kwargs: Additional parameters (not used).

        Returns:
            A tuple containing:

                - The OSM features GeoDataFrame (possibly with reset index)
                - The input `GeoDataFrame` with the new output_column added
                  (filtered if threshold_distance was specified)

        !!! note "To Keep in Mind"

            - [x] The method preferentially uses `OSM IDs` when available, otherwise
              falls back to `DataFrame indices`.
            - [x] The method converts to a projected `CRS` for accurate distance calculations.
        """
        dataframe = data.copy()
        if "geometry" not in dataframe.columns:
            dataframe = gpd.GeoDataFrame(
                dataframe,
                geometry=gpd.points_from_xy(
                    dataframe[longitude_column], dataframe[latitude_column]
                ),
                crs=self.coordinate_reference_system,
            )
        if not dataframe.crs.is_projected:
            utm_crs = dataframe.estimate_utm_crs()
            dataframe = dataframe.to_crs(utm_crs)
            layer_projected = self.layer.to_crs(utm_crs)
        else:
            layer_projected = self.layer

        features_reset = layer_projected.reset_index()
        unique_id = "osmid" if "osmid" in features_reset.columns else "index"

        mapped_data = gpd.sjoin_nearest(
            dataframe,
            features_reset[["geometry", unique_id]],
            how="left",
            max_distance=threshold_distance,
            distance_col="distance_to_feature",
        )
        mapped_data[output_column] = mapped_data[unique_id]
        return self.layer, mapped_data.drop(
            columns=[unique_id, "distance_to_feature", "index_right"],
            errors="ignore",
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call a loading method (e.g., from_place) first.",
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        """Get the loaded `OSM features` layer.

        This method returns the `GeoDataFrame` containing the loaded OSM features.
        It's primarily used for accessing the layer after loading it using
        methods like `from_place`, `from_bbox`, etc.

        Returns:
            The `GeoDataFrame` containing the loaded OSM features.
        """
        return self.layer

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call a loading method (e.g., from_place) first.",
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the loaded `OSM features` layer.

        This method returns the bounding box coordinates of the loaded OSM features
        in the format (`min_lon`, `min_lat`, `max_lon`, `max_lat`). It's useful for
        understanding the spatial extent of the layer.

        Returns:
            A tuple containing the bounding box coordinates in the format
            (`min_lon`, `min_lat`, `max_lon`, `max_lat`).
        """
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call a loading method (e.g., from_place) first.",
    )
    def static_render(self, **plot_kwargs) -> None:
        """Render the loaded `OSM features` layer.

        This method visualises the loaded OSM features using the specified
        plotting parameters. It uses the `plot()` method of the `GeoDataFrame`
        to create a static plot.

        Args:
            **plot_kwargs: Additional parameters passed to the `GeoDataFrame.plot()` method.

        Returns:
            None: The method does not return anything. It directly displays the plot.
        """
        self.layer.plot(**plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        """Preview the loaded `OSM features` layer.

        This method provides a summary of the loaded `OSM features`, including
        the `tags` used for filtering, the `coordinate reference system` (CRS),
        and the `mappings` between the input data and the OSM features.

        Args:
            format: Format of the preview output. Options are "ascii" or "json".
                - [x] "ascii" - Plain text summary.
                - [x] "json" - JSON representation of the summary.

        Returns:
            A string or dictionary containing the preview information.

        Raises:
            ValueError: If an unsupported format is specified.
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
                f"Urban Layer: OSMFeatures\n"
                f"  Focussing tags: {self.tags}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "OSMFeatures",
                "tags": self.tags,
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
