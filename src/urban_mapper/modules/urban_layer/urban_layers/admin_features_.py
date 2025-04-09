from typing import Dict

import geopandas as gpd
from beartype import beartype
import osmnx as ox
from shapely.geometry import Polygon, MultiPolygon


@beartype
class AdminFeatures:
    def __init__(self) -> None:
        self._features: gpd.GeoDataFrame | None = None

    def load(
        self, method: str, tags: Dict[str, str | bool | dict | list], **kwargs
    ) -> None:
        method = method.lower()
        valid_methods = {"address", "bbox", "place", "point", "polygon"}
        if method not in valid_methods:
            raise ValueError(f"Invalid method. Choose from {valid_methods}")

        if method == "address":
            if "address" not in kwargs or "dist" not in kwargs:
                raise ValueError("Method 'address' requires 'address' and 'dist'")
            if "timeout" in kwargs:
                ox.settings.overpass_settings = (
                    f"[out:json][timeout:{kwargs['timeout']}]"
                )
            self._features = ox.features_from_address(
                kwargs["address"], tags, kwargs["dist"]
            )
        elif method == "bbox":
            if "bbox" not in kwargs:
                raise ValueError("Method 'bbox' requires 'bbox'")
            if "timeout" in kwargs:
                ox.settings.overpass_settings = (
                    f"[out:json][timeout:{kwargs['timeout']}]"
                )
            bbox = kwargs["bbox"]
            if not isinstance(bbox, tuple) or len(bbox) != 4:
                raise ValueError("'bbox' must be a tuple of (left, bottom, right, top)")
            self._features = ox.features_from_bbox(bbox, tags)
        elif method == "place":
            if "query" not in kwargs:
                raise ValueError("Method 'place' requires 'query'")
            if "timeout" in kwargs:
                ox.settings.overpass_settings = (
                    f"[out:json][timeout:{kwargs['timeout']}]"
                )
            self._features = ox.features_from_place(kwargs["query"], tags)
        elif method == "point":
            if "center_point" not in kwargs or "dist" not in kwargs:
                raise ValueError("Method 'point' requires 'center_point' and 'dist'")
            if "timeout" in kwargs:
                ox.settings.overpass_settings = (
                    f"[out:json][timeout:{kwargs['timeout']}]"
                )
            self._features = ox.features_from_point(
                kwargs["center_point"], tags, kwargs["dist"]
            )
        elif method == "polygon":
            if "polygon" not in kwargs:
                raise ValueError("Method 'polygon' requires 'polygon'")
            if "timeout" in kwargs:
                ox.settings.overpass_settings = (
                    f"[out:json][timeout:{kwargs['timeout']}]"
                )
            polygon = kwargs["polygon"]
            if not isinstance(polygon, (Polygon, MultiPolygon)):
                raise ValueError("'polygon' must be a shapely Polygon or MultiPolygon")
            self._features = ox.features_from_polygon(polygon, tags)

    @property
    def features(self) -> gpd.GeoDataFrame:
        if self._features is None:
            raise ValueError("Features not loaded. Call load() first.")
        return self._features
