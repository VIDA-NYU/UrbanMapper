from typing import Tuple, Dict, Any
from pathlib import Path
from beartype import beartype
from shapely.geometry import Polygon, MultiPolygon
from shapely.wkt import loads
from geopy.geocoders import Nominatim
import warnings
import geopandas as gpd

from .admin_features_ import AdminFeatures
from .osm_features import OSMFeatures
from urban_mapper import logger


@beartype
class AdminRegions(OSMFeatures):
    """Base class for `administrative regions` at `various levels`.

    !!! warning "What to understand from this class?"
        In a nutshell? You barely will be using this out at all, unless you create a new
        `UrbanLayer` that needs to load `OpenStreetMap` features. If not, you can skip reading.

    This abstract class provides shared functionality for `loading` and `processing`
    `administrative boundaries` from `OpenStreetMap`. It's designed to be subclassed
    for specific types of administrative regions (`neighborhoods`, `cities`, `states`, `countries`).

    The class _intelligently_ handles the complexities of `OpenStreetMap's administrative
    levels`, which vary across different `countries` and `regions`. It attempts to infer
    the appropriate level based on the type of administrative division requested,
    but also allows manual overriding of this inference.

    Further can be read at: [OpenStreetMap Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative)
    to understand why it is complex to infer the right `admin_level`.

    Attributes:
        division_type: The type of administrative division this layer represents
            (e.g., "neighborhood", "city", "state", "country").
        tags: OpenStreetMap tags used to filter boundary features.
        layer: The GeoDataFrame containing the administrative boundary data (set after loading).

    Examples:
        >>> # This is an abstract class - use concrete implementations like:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> # For neighborhoods:
        >>> neighborhoods = mapper.urban_layer.region_neighborhoods().from_place("Paris, France")
        >>> # For cities:
        >>> cities = mapper.urban_layer.region_cities().from_place("Hérault, France")
    """

    def __init__(self) -> None:
        super().__init__()
        self.division_type: str | None = None
        self.tags: Dict[str, str] | None = None

    def from_place(
        self, place_name: str, overwrite_admin_level: str | None = None, **kwargs
    ) -> None:
        """Load `administrative regions` for a named place.

        This method retrieves administrative boundaries for a specified place
        name from `OpenStreetMap`. It filters for the appropriate `administrative
        level` based on the division_type set for this layer, and can be manually
        overridden if needed.

        Args:
            place_name: Name of the place to load administrative regions for
                (e.g., "New York City", "Bavaria, Germany").
            overwrite_admin_level: Manually specify the OpenStreetMap admin_level
                to use instead of inferring it. Admin levels differ by region but
                typically follow patterns like:

                - [x] 2: Country
                - [x] 4: State/Province
                - [x] 6: County
                - [x] 8: City/Municipality
                - [x] 10: Neighborhood/Borough

                Feel free to look into [OSM Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative).

            **kwargs: Additional parameters passed to OSMnx's features_from_place.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If division_type is not set or if no administrative
                boundaries are found for the specified place.

        Examples:
            >>> # Get neighborhoods in Manhattan
            >>> neighborhoods = AdminRegions()
            >>> neighborhoods.division_type = "neighborhood"
            >>> neighborhoods.from_place("Manhattan, New York")

            >>> # Override admin level for more control
            >>> cities = AdminRegions()
            >>> cities.division_type = "city"
            >>> cities.from_place("France", overwrite_admin_level="6")
        """
        if self.division_type is None:
            raise ValueError("Division type not set for this layer.")
        warnings.warn(
            "Administrative levels vary across regions. The system will infer the most appropriate admin_level "
            "based on the data and division type, but you can (and is recommended to) override it "
            "with 'overwrite_admin_level'."
        )
        geolocator = Nominatim(user_agent="urban_mapper")
        place_polygon = None
        try:
            location = geolocator.geocode(place_name, geometry="wkt")
            if location and "geotext" in location.raw:
                place_polygon = loads(location.raw["geotext"])
            else:
                logger.log(
                    "DEBUG_LOW", f"Geocoding for {place_name} did not return a polygon."
                )
        except Exception as e:
            logger.log(
                "DEBUG_LOW",
                f"Geocoding failed for {place_name}: {e}. Proceeding without polygon filtering.",
            )
        self.tags = {"boundary": "administrative"}
        self.feature_network = AdminFeatures()
        self.feature_network.load("place", self.tags, query=place_name, **kwargs)
        all_boundaries = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )
        if place_polygon:
            all_boundaries = all_boundaries[
                all_boundaries.geometry.within(place_polygon)
            ]
            if all_boundaries.empty:
                logger.log(
                    "DEBUG_LOW",
                    "No boundaries found within the geocoded polygon. Using all loaded boundaries.",
                )
                all_boundaries = self.feature_network.features.to_crs(
                    self.coordinate_reference_system
                )
        all_boundaries.reset_index(inplace=True)
        if (
            "element" in all_boundaries.columns
            and "relation" in all_boundaries["element"].unique()
        ):
            all_boundaries = all_boundaries[all_boundaries["element"] == "relation"]
        else:
            logger.log(
                "DEBUG_LOW",
                "No 'relation' found in 'element' column. Using all loaded boundaries.",
            )
        available_levels = all_boundaries["admin_level"].dropna().unique()
        if not available_levels.size:
            raise ValueError(f"No administrative boundaries found for {place_name}.")
        if overwrite_admin_level is not None:
            logger.log(
                "DEBUG_LOW", f"Admin level overridden to {overwrite_admin_level}."
            )
            if overwrite_admin_level not in available_levels:
                raise ValueError(
                    f"Overridden admin level {overwrite_admin_level} not found in available levels: {available_levels}."
                )
            admin_level = overwrite_admin_level
        else:
            inferred_level = self.infer_best_admin_level(
                all_boundaries.copy(), self.division_type
            )
            warnings.warn(
                f"Inferred admin_level for {self.division_type}: {inferred_level}. "
                f"Other available levels: {sorted(available_levels)}. "
                "You can override this with 'overwrite_admin_level' if desired."
            )
            admin_level = inferred_level
        self.layer = all_boundaries[
            all_boundaries["admin_level"] == admin_level
        ].to_crs(self.coordinate_reference_system)

    def from_address(
        self,
        address: str,
        dist: float,
        overwrite_admin_level: str | None = None,
        **kwargs,
    ) -> None:
        """Load `administrative regions` for a specific address.

        This method retrieves administrative boundaries for a specified address
        from `OpenStreetMap`. It filters for the appropriate `administrative
        level` based on the division_type set for this layer, and can be manually
        overridden if needed.

        Args:
            address: Address to load administrative regions for (e.g., "1600 Amphitheatre Parkway, Mountain View, CA").
            dist: Distance in meters to search around the address. Consider this a radius.
            overwrite_admin_level: Manually specify the OpenStreetMap admin_level
                to use instead of inferring it. Admin levels differ by region but
                typically follow patterns like:

                - [x] 2: Country
                - [x] 4: State/Province
                - [x] 6: County
                - [x] 8: City/Municipality
                - [x] 10: Neighborhood/Borough

                Feel free to look into [OSM Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative).

            **kwargs: Additional parameters passed to OSMnx's features_from_address.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If division_type is not set or if no administrative
                boundaries are found for the specified address.

        Examples:
            >>> # Get neighborhoods around a specific address
            >>> neighborhoods = AdminRegions()
            >>> neighborhoods.division_type = "neighborhood"
            >>> neighborhoods.from_address("1600 Amphitheatre Parkway, Mountain View, CA", dist=500)

            >>> # Override admin level for more control
            >>> cities = AdminRegions()
            >>> cities.division_type = "city"
            >>> cities.from_address("1600 Amphitheatre Parkway, Mountain View, CA", dist=500, overwrite_admin_level="6")
        """

        if self.division_type is None:
            raise ValueError("Division type not set for this layer.")
        warnings.warn(
            "Administrative levels vary across regions. The system will infer the most appropriate admin_level "
            "based on the data and division type, but you can (and is recommended to) override it "
            "with 'overwrite_admin_level'."
        )
        geolocator = Nominatim(user_agent="urban_mapper")
        place_polygon = None
        try:
            location = geolocator.geocode(address, geometry="wkt")
            if location and "geotext" in location.raw:
                place_polygon = loads(location.raw["geotext"])
            else:
                logger.log(
                    "DEBUG_LOW", f"Geocoding for {address} did not return a polygon."
                )
        except Exception as e:
            logger.log(
                "DEBUG_LOW",
                f"Geocoding failed for {address}: {e}. Proceeding without polygon filtering.",
            )
        self.tags = {"boundary": "administrative"}
        self.feature_network = AdminFeatures()
        self.feature_network.load(
            "address", self.tags, address=address, dist=dist, **kwargs
        )
        all_boundaries = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )
        if place_polygon:
            all_boundaries = all_boundaries[
                all_boundaries.geometry.within(place_polygon)
            ]
            if all_boundaries.empty:
                logger.log(
                    "DEBUG_LOW",
                    "No boundaries found within the geocoded polygon. Using all loaded boundaries.",
                )
                all_boundaries = self.feature_network.features.to_crs(
                    self.coordinate_reference_system
                )
        all_boundaries.reset_index(inplace=True)
        if (
            "element" in all_boundaries.columns
            and "relation" in all_boundaries["element"].unique()
        ):
            all_boundaries = all_boundaries[all_boundaries["element"] == "relation"]
        else:
            logger.log(
                "DEBUG_LOW",
                "No 'relation' found in 'element' column. Using all loaded boundaries.",
            )
        available_levels = all_boundaries["admin_level"].dropna().unique()
        if not available_levels.size:
            raise ValueError(
                f"No administrative boundaries found for address {address}."
            )
        if overwrite_admin_level is not None:
            logger.log(
                "DEBUG_LOW", f"Admin level overridden to {overwrite_admin_level}."
            )
            if overwrite_admin_level not in available_levels:
                raise ValueError(
                    f"Overridden admin level {overwrite_admin_level} not found in available levels: {available_levels}."
                )
            admin_level = overwrite_admin_level
        else:
            inferred_level = self.infer_best_admin_level(
                all_boundaries.copy(), self.division_type
            )
            warnings.warn(
                f"Inferred admin_level for {self.division_type}: {inferred_level}. "
                f"Other available levels: {sorted(available_levels)}. "
                "You can override this with 'overwrite_admin_level' if desired."
            )
            admin_level = inferred_level
        self.layer = all_boundaries[
            all_boundaries["admin_level"] == admin_level
        ].to_crs(self.coordinate_reference_system)

    def from_polygon(
        self,
        polygon: Polygon | MultiPolygon,
        overwrite_admin_level: str | None = None,
        **kwargs,
    ) -> None:
        """Load `administrative regions` for a specific polygon.
        This method retrieves administrative boundaries for a specified polygon
        from `OpenStreetMap`. It filters for the appropriate `administrative
        level` based on the division_type set for this layer, and can be manually
        overridden if needed.

        Args:
            polygon: Shapely Polygon or MultiPolygon to load administrative regions for.
            overwrite_admin_level: Manually specify the OpenStreetMap admin_level
                to use instead of inferring it. Admin levels differ by region but
                typically follow patterns like:

                - [x] 2: Country
                - [x] 4: State/Province
                - [x] 6: County
                - [x] 8: City/Municipality
                - [x] 10: Neighborhood/Borough

                Feel free to look into [OSM Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative).

            **kwargs: Additional parameters passed to OSMnx's features_from_polygon.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If division_type is not set or if no administrative
                boundaries are found for the specified polygon.

        Examples:
            >>> # Create a polygon out of an address for instance, with the help of geopy
            >>> from geopy.geocoders import Nominatim
            >>> geolocator = Nominatim(user_agent="urban_mapper")
            >>> location = geolocator.geocode("1600 Amphitheatre Parkway, Mountain View, CA", geometry="wkt")
            >>> polygon = loads(location.raw["geotext"])

            >>> # Get neighborhoods within a specific polygon
            >>> neighborhoods = AdminRegions()
            >>> neighborhoods.division_type = "neighborhood"
            >>> neighborhoods.from_polygon(polygon)

            >>> # Override admin level for more control
            >>> cities = AdminRegions()
            >>> cities.division_type = "neighborhood"
            >>> cities.from_polygon(polygon, overwrite_admin_level="8")
        """

        if self.division_type is None:
            raise ValueError("Division type not set for this layer.")
        warnings.warn(
            "Administrative levels vary across regions. The system will infer the most appropriate admin_level "
            "based on the data and division type, but you can (and is recommended to) override it "
            "with 'overwrite_admin_level'."
        )
        self.tags = {"boundary": "administrative"}
        self.feature_network = AdminFeatures()
        self.feature_network.load("polygon", self.tags, polygon=polygon, **kwargs)
        all_boundaries = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )
        all_boundaries = all_boundaries[all_boundaries.geometry.within(polygon)]
        if all_boundaries.empty:
            logger.log(
                "DEBUG_LOW",
                "No boundaries found within the provided polygon. Using all loaded boundaries.",
            )
            all_boundaries = self.feature_network.features.to_crs(
                self.coordinate_reference_system
            )
        all_boundaries.reset_index(inplace=True)
        if (
            "element" in all_boundaries.columns
            and "relation" in all_boundaries["element"].unique()
        ):
            all_boundaries = all_boundaries[all_boundaries["element"] == "relation"]
        else:
            logger.log(
                "DEBUG_LOW",
                "No 'relation' found in 'element' column. Using all loaded boundaries.",
            )
        available_levels = all_boundaries["admin_level"].dropna().unique()
        if not available_levels.size:
            raise ValueError(
                "No administrative boundaries found within the provided polygon."
            )
        if overwrite_admin_level is not None:
            logger.log(
                "DEBUG_LOW", f"Admin level overridden to {overwrite_admin_level}."
            )
            if overwrite_admin_level not in available_levels:
                raise ValueError(
                    f"Overridden admin level {overwrite_admin_level} not found in available levels: {available_levels}."
                )
            admin_level = overwrite_admin_level
        else:
            inferred_level = self.infer_best_admin_level(
                all_boundaries.copy(), self.division_type
            )
            warnings.warn(
                f"Inferred admin_level for {self.division_type}: {inferred_level}. "
                f"Other available levels: {sorted(available_levels)}. "
                "You can override this with 'overwrite_admin_level' if desired."
            )
            admin_level = inferred_level
        self.layer = all_boundaries[
            all_boundaries["admin_level"] == admin_level
        ].to_crs(self.coordinate_reference_system)

    def from_bbox(
        self,
        bbox: Tuple[float, float, float, float],
        overwrite_admin_level: str | None = None,
        **kwargs,
    ) -> None:
        """Load `administrative regions` for a specific bounding box.
        This method retrieves administrative boundaries for a specified bounding
        box from `OpenStreetMap`. It filters for the appropriate `administrative
        level` based on the division_type set for this layer, and can be manually
        overridden if needed.

        Args:
            bbox: Tuple of (left, bottom, right, top) coordinates defining the bounding box.
            overwrite_admin_level: Manually specify the OpenStreetMap admin_level
                to use instead of inferring it. Admin levels differ by region but
                typically follow patterns like:

                - [x] 2: Country
                - [x] 4: State/Province
                - [x] 6: County
                - [x] 8: City/Municipality
                - [x] 10: Neighborhood/Borough

                Feel free to look into [OSM Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative).

            **kwargs: Additional parameters passed to OSMnx's features_from_bbox.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If division_type is not set or if no administrative
                boundaries are found for the specified bounding box.

        Examples:
            >>> # Get neighborhoods within a specific bounding box
            >>> bbox = (-73.935242, 40.730610, -73.925242, 40.740610)  # Example coordinates
            >>> neighborhoods = AdminRegions()
            >>> neighborhoods.division_type = "neighborhood"
            >>> neighborhoods.from_bbox(bbox)

            >>> # Override admin level for more control
            >>> cities = AdminRegions()
            >>> cities.division_type = "city"
            >>> cities.from_bbox(bbox, overwrite_admin_level="8")
        """
        if self.division_type is None:
            raise ValueError("Division type not set for this layer.")
        warnings.warn(
            "Administrative levels vary across regions. The system will infer the most appropriate admin_level "
            "based on the data and division type, but you can (and is recommended to) override it "
            "with 'overwrite_admin_level'."
        )
        self.tags = {"boundary": "administrative"}
        self.feature_network = AdminFeatures()
        self.feature_network.load("bbox", self.tags, bbox=bbox, **kwargs)
        all_boundaries = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )
        all_boundaries.reset_index(inplace=True)
        if (
            "element" in all_boundaries.columns
            and "relation" in all_boundaries["element"].unique()
        ):
            all_boundaries = all_boundaries[all_boundaries["element"] == "relation"]
        else:
            logger.log(
                "DEBUG_LOW",
                "No 'relation' found in 'element' column. Using all loaded boundaries.",
            )
        available_levels = all_boundaries["admin_level"].dropna().unique()
        if not available_levels.size:
            raise ValueError(
                "No administrative boundaries found within the provided bounding box."
            )
        if overwrite_admin_level is not None:
            logger.log(
                "DEBUG_LOW", f"Admin level overridden to {overwrite_admin_level}."
            )
            if overwrite_admin_level not in available_levels:
                raise ValueError(
                    f"Overridden admin level {overwrite_admin_level} not found in available levels: {available_levels}."
                )
            admin_level = overwrite_admin_level
        else:
            inferred_level = self.infer_best_admin_level(
                all_boundaries.copy(), self.division_type
            )
            warnings.warn(
                f"Inferred admin_level for {self.division_type}: {inferred_level}. "
                f"Other available levels: {sorted(available_levels)}. "
                "You can override this with 'overwrite_admin_level' if desired."
            )
            admin_level = inferred_level
        self.layer = all_boundaries[
            all_boundaries["admin_level"] == admin_level
        ].to_crs(self.coordinate_reference_system)

    def from_point(
        self,
        lat: float,
        lon: float,
        dist: float,
        overwrite_admin_level: str | None = None,
        **kwargs,
    ) -> None:
        """Load `administrative regions` for a specific point.
        This method retrieves administrative boundaries for a specified point
        from `OpenStreetMap`. It filters for the appropriate `administrative
        level` based on the division_type set for this layer, and can be manually
        overridden if needed.

        Args:
            lat: Latitude of the point to load administrative regions for.
            lon: Longitude of the point to load administrative regions for.
            dist: Distance in meters to search around the point. Consider this a radius.
            overwrite_admin_level: Manually specify the OpenStreetMap admin_level
                to use instead of inferring it. Admin levels differ by region but
                typically follow patterns like:

                - [x] 2: Country
                - [x] 4: State/Province
                - [x] 6: County
                - [x] 8: City/Municipality
                - [x] 10: Neighborhood/Borough

                Feel free to look into [OSM Wiki](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative).

            **kwargs: Additional parameters passed to OSMnx's features_from_point.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If division_type is not set or if no administrative
                boundaries are found for the specified point.

        Examples:
            >>> # Get neighborhoods around a specific point
            >>> neighborhoods = AdminRegions()
            >>> neighborhoods.division_type = "neighborhood"
            >>> neighborhoods.from_point(40.730610, -73.935242, dist=500)

            >>> # Override admin level for more control
            >>> cities = AdminRegions()
            >>> cities.division_type = "city"
            >>> cities.from_point(40.730610, -73.935242, dist=500, overwrite_admin_level="8")
        """
        if self.division_type is None:
            raise ValueError("Division type not set for this layer.")
        warnings.warn(
            "Administrative levels vary across regions. The system will infer the most appropriate admin_level "
            "based on the data and division type, but you can (and is recommended to) override it "
            "with 'overwrite_admin_level'."
        )
        self.tags = {"boundary": "administrative"}
        self.feature_network = AdminFeatures()
        self.feature_network.load(
            "point", self.tags, lat=lat, lon=lon, dist=dist, **kwargs
        )
        all_boundaries = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )
        all_boundaries.reset_index(inplace=True)
        if (
            "element" in all_boundaries.columns
            and "relation" in all_boundaries["element"].unique()
        ):
            all_boundaries = all_boundaries[all_boundaries["element"] == "relation"]
        else:
            logger.log(
                "DEBUG_LOW",
                "No 'relation' found in 'element' column. Using all loaded boundaries.",
            )
        available_levels = all_boundaries["admin_level"].dropna().unique()
        if not available_levels.size:
            raise ValueError(
                "No administrative boundaries found around the provided point."
            )
        if overwrite_admin_level is not None:
            logger.log(
                "DEBUG_LOW", f"Admin level overridden to {overwrite_admin_level}."
            )
            if overwrite_admin_level not in available_levels:
                raise ValueError(
                    f"Overridden admin level {overwrite_admin_level} not found in available levels: {available_levels}."
                )
            admin_level = overwrite_admin_level
        else:
            inferred_level = self.infer_best_admin_level(
                all_boundaries.copy(), self.division_type
            )
            warnings.warn(
                f"Inferred admin_level for {self.division_type}: {inferred_level}. "
                f"Other available levels: {sorted(available_levels)}. "
                "You can override this with 'overwrite_admin_level' if desired."
            )
            admin_level = inferred_level
        self.layer = all_boundaries[
            all_boundaries["admin_level"] == admin_level
        ].to_crs(self.coordinate_reference_system)

    def infer_best_admin_level(
        self, boundaries: gpd.GeoDataFrame, division_type: str
    ) -> str:
        """Infer the most appropriate `OpenStreetMap admin_level` for a division type.

        This method uses heuristics to determine which `administrative level` in
        `OpenStreetMap` best matches the requested division type (`neighborhood`, `city`,
        `state`, or `country`). It accounts for both the number of regions at each level
        and their spatial connectivity patterns.

        The method calculates a score for each available admin_level based on:

        - [x] The number of regions (higher for `neighborhoods`, lower for countries)
        - [x] The connectivity between regions (how many `share boundaries`)
        - [x] The specific division type requested, i.e., `neighborhood`, `city`, `state`, or `country`.

        !!! note "Why is this heuristic?"
            This method is intentionally heuristic because `OSM admin_levels` vary
            across `regions` and `countries`. The scoring system prioritises different
            factors based on the division type, as follows:

            - [x] `Neighborhoods`: High region count, moderate connectivity
            - [x] `Cities`: Moderate region count, high connectivity
            - [x] `States`: Low region count, high connectivity
            - [x] `Countries`: Very low region count, very high connectivity

        Args:
            boundaries: `GeoDataFrame` containing administrative boundaries with
                an "admin_level" column.
            division_type: The type of division to find the best level for
                (`neighborhood`, `city`, `state`, or `country`).

        Returns:
            The `admin_level` string that best matches the requested division type.

        Raises:
            ValueError: If the division_type is not recogniseed.
        """
        levels = boundaries["admin_level"].unique()
        metrics = {}
        for level in levels:
            level_gdf = boundaries[boundaries["admin_level"] == level]
            connectivity = self._calculate_connectivity(level_gdf)
            count = len(level_gdf)
            if division_type == "neighborhood":
                score = (count / boundaries.shape[0]) * 100 + connectivity * 0.5
            elif division_type == "city":
                score = (count / boundaries.shape[0]) * 50 + connectivity * 0.75
            elif division_type == "state":
                score = connectivity * 1.0 - (count / boundaries.shape[0]) * 20
            elif division_type == "country":
                score = connectivity * 1.5 - (count / boundaries.shape[0]) * 10
            else:
                raise ValueError(f"Unknown division_type: {division_type}")
            metrics[level] = score
            logger.log(
                "DEBUG_LOW",
                f"Admin level {level}: count={count}, "
                f"connectivity={connectivity:.2f}%, "
                f"score={score:.2f}",
            )
        return max(metrics, key=metrics.get)

    def from_file(
        self, file_path: str | Path, overwrite_admin_level: str | None = None, **kwargs
    ) -> None:
        """Load `administrative regions` from a file.

        !!! warning "Not implemented"
            This method is not implemented for this class. It raises a `NotImplementedError`
            to indicate that loading administrative regions from a file is not supported.

        Args:
            file_path: Path to the file containing administrative regions data.
            overwrite_admin_level: (Optional) Manually specify the OpenStreetMap admin_level
                to use instead of inferring it. Admin levels differ by region but
                typically follow patterns like:

                - [x] 2: Country
                - [x] 4: State/Province
                - [x] 6: County
                - [x] 8: City/Municipality
                - [x] 10: Neighborhood/Borough

            **kwargs: Additional parameters passed to OSMnx's features_from_file.


        Raises:
            NotImplementedError: This method is not implemented for this class.

        Examples:
            >>> # Load administrative regions from a file (not implemented)
            >>> admin_regions = AdminRegions()
            >>> admin_regions.from_file("path/to/file.geojson")
        """
        raise NotImplementedError(
            "Loading administrative regions from file is not supported."
        )

    def preview(self, format: str = "ascii") -> Any:
        """Preview the `urban layer` in a human-readable format.

        This method provides a summary of the `urban layer` attributes, including
        the division type, tags, coordinate reference system, and mappings.
        It can return the preview in either ASCII or JSON format.

        Args:
            format: The format for the preview. Can be "ascii" or "json". Default is "ascii".

        Returns:
            A string or dictionary containing the preview of the urban layer.
            If format is "ascii", returns a formatted string. If format is "json",
            returns a dictionary.

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
                f"Urban Layer: Region_{self.division_type}\n"
                f"  Focussing tags: {self.tags}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": f"Region_{self.division_type}",
                "tags": self.tags,
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")

    def _calculate_connectivity(self, gdf: gpd.GeoDataFrame) -> float:
        """Calculate the `spatial connectivity` percentage for a set of polygons.

        !!! note "What is spatial connectivity?"
            Spatial connectivity refers to the degree to which polygons in a
            geographic dataset are adjacent or overlapping with each other.

            In the context of administrative boundaries, it indicates how
            well-defined and interconnected the regions are. A high connectivity
            percentage suggests that the polygons are closely related and
            form a coherent administrative structure, while a low percentage
            may indicate isolated or poorly defined regions.

            Note that this method is not a strict measure of connectivity but rather
            an approximation based on the number of polygons that share boundaries.

            Lastly, note that this is also a `static` method, consider this as an helper to only
            use within the class.

        Args:
            gdf: `GeoDataFrame` containing polygon geometries to analyze.

        Returns:
            Percentage (0-100) of polygons that touch or overlap with at least
            one other polygon in the dataset.
        """
        if len(gdf) < 2:
            return 0.0
        sindex = gdf.sindex
        touching_count = 0
        for idx, geom in gdf.iterrows():
            possible_matches_index = list(sindex.intersection(geom.geometry.bounds))
            possible_matches = gdf.iloc[possible_matches_index]
            possible_matches = possible_matches[possible_matches.index != idx]
            if any(
                geom.geometry.touches(match.geometry)
                or geom.geometry.overlaps(match.geometry)
                for _, match in possible_matches.iterrows()
            ):
                touching_count += 1
        return (touching_count / len(gdf)) * 100
