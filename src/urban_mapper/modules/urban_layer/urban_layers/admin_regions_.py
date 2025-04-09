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
    def __init__(self) -> None:
        super().__init__()
        self.division_type: str | None = None
        self.tags: Dict[str, str] | None = None

    def from_place(
        self, place_name: str, overwrite_admin_level: str | None = None, **kwargs
    ) -> None:
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
        best_level = max(metrics, key=metrics.get)
        return best_level

    def from_file(
        self, file_path: str | Path, overwrite_admin_level: str | None = None, **kwargs
    ) -> None:
        raise NotImplementedError(
            "Loading administrative regions from file is not supported."
        )

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
