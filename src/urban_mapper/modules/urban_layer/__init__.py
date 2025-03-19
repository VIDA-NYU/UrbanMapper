from .urban_layers import (
    OSMNXStreets,
    OSMNXIntersections,
    Tile2NetSidewalks,
    Tile2NetCrosswalks,
    OSMFeatures,
)

from .urban_layer_factory import UrbanLayerFactory

from .abc_urban_layer import UrbanLayerBase

URBAN_LAYER_FACTORY = {
    "streets_roads": OSMNXStreets,
    "streets_intersections": OSMNXIntersections,
    "streets_sidewalks": Tile2NetSidewalks,
    "streets_crosswalks": Tile2NetCrosswalks,
    "streets_features": OSMFeatures,
}

__all__ = [
    "UrbanLayerBase",
    "OSMNXStreets",
    "OSMNXIntersections",
    "Tile2NetSidewalks",
    "Tile2NetCrosswalks",
    "OSMFeatures",
    "URBAN_LAYER_FACTORY",
    "UrbanLayerFactory",
]
