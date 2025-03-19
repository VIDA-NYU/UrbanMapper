from typing import Tuple, Dict, Any
import geopandas as gpd
from pathlib import Path
from beartype import beartype

from urban_mapper.utils import require_attributes_not_none
from ..abc_urban_layer import UrbanLayerBase

import osmnx as ox
from shapely.geometry import Polygon, MultiPolygon


@beartype
class FeatureNetwork:
    def __init__(self) -> None:
        self._features: gpd.GeoDataFrame | None = None

    def load(self, method: str, tags: Dict[str, str | bool], **kwargs) -> None:
        method = method.lower()
        valid_methods = {"address", "bbox", "place", "point", "polygon"}
        if method not in valid_methods:
            raise ValueError(f"Invalid method. Choose from {valid_methods}")

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
        if self._features is None:
            raise ValueError("Features not loaded. Call load() first.")
        return self._features


@beartype
class OSMFeatures(UrbanLayerBase):
    def __init__(self) -> None:
        super().__init__()
        self.feature_network: FeatureNetwork | None = None
        self.tags: Dict[str, str] | None = None

    def from_place(
        self, place_name: str, tags: Dict[str, str | bool], **kwargs
    ) -> None:
        self.tags = tags
        self.feature_network = FeatureNetwork()
        self.feature_network.load("place", tags, query=place_name, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_address(
        self, address: str, tags: Dict[str, str | bool], dist: float, **kwargs
    ) -> None:
        self.tags = tags
        self.feature_network = FeatureNetwork()
        self.feature_network.load("address", tags, address=address, dist=dist, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_bbox(
        self,
        bbox: Tuple[float, float, float, float],
        tags: Dict[str, str | bool],
        **kwargs,
    ) -> None:
        self.tags = tags
        self.feature_network = FeatureNetwork()
        self.feature_network.load("bbox", tags, bbox=bbox, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_point(
        self,
        center_point: Tuple[float, float],
        tags: Dict[str, str | bool],
        dist: float,
        **kwargs,
    ) -> None:
        self.tags = tags
        self.feature_network = FeatureNetwork()
        self.feature_network.load(
            "point", tags, center_point=center_point, dist=dist, **kwargs
        )
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_polygon(
        self, polygon: Polygon | MultiPolygon, tags: Dict[str, str | bool], **kwargs
    ) -> None:
        self.tags = tags
        self.feature_network = FeatureNetwork()
        self.feature_network.load("polygon", tags, polygon=polygon, **kwargs)
        self.layer = self.feature_network.features.to_crs(
            self.coordinate_reference_system
        )

    def from_file(self, file_path: str | Path, **kwargs) -> None:
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
            columns=[unique_id, "distance_to_feature", "index_right"]
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call a loading method (e.g., from_place) first.",
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        return self.layer

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call a loading method (e.g., from_place) first.",
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call a loading method (e.g., from_place) first.",
    )
    def static_render(self, **plot_kwargs) -> None:
        self.layer.plot(**plot_kwargs)

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
