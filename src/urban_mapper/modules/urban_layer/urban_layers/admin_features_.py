from typing import Dict

import geopandas as gpd
from beartype import beartype
import osmnx as ox
from shapely.geometry import Polygon, MultiPolygon


@beartype
class AdminFeatures:
    """Helper class for dealing with `OpenStreetMap features`.

    !!! warning "What to understand from this class?"
        In a nutshell? You barely will be using this out at all, unless you create a new
        `UrbanLayer` that needs to load `OpenStreetMap` features. If not, you can skip reading.

    This class provides methods for loading various types of features from `OpenStreetMap`
    using different spatial queries. `Features` can include `amenities` (`restaurants`, `hospitals`),
    `buildings`, `infrastructure`, `natural features`, and more, specified through `OSM tags`.

    More can be found at: [Map Features](https://wiki.openstreetmap.org/wiki/Map_features).

    The class uses `OSMnx`'s `features_from_*` methods to retrieve the data and store it in
    a `GeoDataFrame`. It supports loading features by `place name`, `address`, `bounding box`,
    point with radius, or custom polygon.

    Attributes:
        _features: Internal GeoDataFrame containing the loaded OSM features.
            None until load() is called.

    Examples:
        >>> admin_features = AdminFeatures()
        >>> # Load all restaurants in Manhattan
        >>> tags = {"amenity": "restaurant"}
        >>> admin_features.load("place", tags, query="Manhattan, New York")
        >>> restaurants = admin_features.features
    """

    def __init__(self) -> None:
        self._features: gpd.GeoDataFrame | None = None

    def load(
        self, method: str, tags: Dict[str, str | bool | dict | list], **kwargs
    ) -> None:
        """Load `OpenStreetMap` features using the specified method and tags.

        This method retrieves features from `OpenStreetMap` that match the provided
        tags, using one of several spatial query methods (`address`, `bbox`, `place`, `point`,
        or `polygon`). The specific parameters required depend on the method chosen.e

        Args:
            method: The spatial query method to use. One of:
                - "address": Load features around an address
                - "bbox": Load features within a bounding box
                - "place": Load features for a named place (city, neighborhood, etc.)
                - "point": Load features around a specific point
                - "polygon": Load features within a polygon
            tags: Dictionary specifying the OpenStreetMap tags to filter features.
                Examples:
                - {"amenity": "restaurant"} - All restaurants
                - {"building": True} - All buildings
                - {"leisure": ["park", "garden"]} - Parks and gardens
                - {"landuse": "residential"} - Residential areas
            **kwargs: Additional arguments specific to the chosen method:
                - address: Requires "address" (str) and "dist" (float)
                - bbox: Requires "bbox" (tuple of left, bottom, right, top)
                - place: Requires "query" (str)
                - point: Requires "center_point" (tuple of lat, lon) and "dist" (float)
                - polygon: Requires "polygon" (Shapely Polygon/MultiPolygon)
                - All methods: Optional "timeout" (int) for Overpass API timeout in seconds

        Raises:
            ValueError: If an invalid method is specified or required parameters are missing

        Examples:
            >>> # Load all parks in Brooklyn
            >>> admin_features = AdminFeatures()
            >>> admin_features.load(
            ...     "place",
            ...     {"leisure": "park"},
            ...     query="Brooklyn, New York"
            ... )

            >>> # Load all hospitals within 5km of a point
            >>> admin_features.load(
            ...     "point",
            ...     {"amenity": "hospital"},
            ...     center_point=(40.7128, -74.0060),  # New York City coordinates
            ...     dist=5000  # 5km radius
            ... )
        """
        method = method.lower()
        valid_methods = {"address", "bbox", "place", "point", "polygon"}
        if method not in valid_methods:
            raise ValueError(f"Invalid method. Choose from {valid_methods}")

        if "timeout" in kwargs:
            ox.settings.overpass_settings = f"[out:json][timeout:{kwargs['timeout']}]"

        if method == "address":
            if "address" not in kwargs or "dist" not in kwargs:
                raise ValueError("Method 'address' requires 'address' and 'dist'")
            self._features = ox.features_from_address(
                kwargs["address"], tags, kwargs["dist"]
            )
        elif method == "bbox":
            if "bbox" not in kwargs:
                raise ValueError("Method 'bbox' requires 'bbox'")
            bbox = kwargs["bbox"]
            if not isinstance(bbox, tuple) or len(bbox) != 4:
                raise ValueError("'bbox' must be a tuple of (left, bottom, right, top)")
            self._features = ox.features_from_bbox(bbox, tags)
        elif method == "place":
            if "query" not in kwargs:
                raise ValueError("Method 'place' requires 'query'")
            self._features = ox.features_from_place(kwargs["query"], tags)
        elif method == "point":
            if "center_point" not in kwargs or "dist" not in kwargs:
                raise ValueError("Method 'point' requires 'center_point' and 'dist'")
            self._features = ox.features_from_point(
                kwargs["center_point"], tags, kwargs["dist"]
            )
        elif method == "polygon":
            if "polygon" not in kwargs:
                raise ValueError("Method 'polygon' requires 'polygon'")
            polygon = kwargs["polygon"]
            if not isinstance(polygon, (Polygon, MultiPolygon)):
                raise ValueError("'polygon' must be a shapely Polygon or MultiPolygon")
            self._features = ox.features_from_polygon(polygon, tags)

    @property
    def features(self) -> gpd.GeoDataFrame:
        """Get the loaded `OpenStreetMap` features as a `GeoDataFrame`.

        This property provides access to the `OpenStreetMap` features that were
        loaded using the `load()` method. The returned `GeoDataFrame` contains
        geometries and attributes for all features that matched the specified tags.

        Returns:
            GeoDataFrame containing the loaded OpenStreetMap features.

        Raises:
            ValueError: If features have not been loaded yet.

        Examples:
            >>> admin_features = AdminFeatures()
            >>> admin_features.load("place", {"amenity": "school"}, query="Boston, MA")
            >>> schools = admin_features.features
            >>> print(f"Found {len(schools)} schools in Boston")
        """
        if self._features is None:
            raise ValueError("Features not loaded. Call load() first.")
        return self._features
