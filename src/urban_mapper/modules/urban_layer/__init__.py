from .urban_layers import (
    OSMNXStreets,
    OSMNXIntersections,
    Tile2NetSidewalks,
    Tile2NetCrosswalks,
    OSMFeatures,
    RegionCities,
    RegionNeighborhoods,
    RegionStates,
    RegionCountries,
    CustomUrbanLayer,
    AdminFeatures,
    AdminRegions,
)

from .urban_layer_factory import UrbanLayerFactory

from .abc_urban_layer import UrbanLayerBase

URBAN_LAYER_FACTORY = {
    "streets_roads": OSMNXStreets,
    "streets_intersections": OSMNXIntersections,
    "streets_sidewalks": Tile2NetSidewalks,
    "streets_crosswalks": Tile2NetCrosswalks,
    "streets_features": OSMFeatures,
    "region_cities": RegionCities,
    "region_neighborhoods": RegionNeighborhoods,
    "region_states": RegionStates,
    "region_countries": RegionCountries,
    "custom_urban_layer": CustomUrbanLayer,
}
__all__ = [
    "UrbanLayerBase",
    "OSMNXStreets",
    "OSMNXIntersections",
    "Tile2NetSidewalks",
    "Tile2NetCrosswalks",
    "OSMFeatures",
    "RegionCities",
    "RegionNeighborhoods",
    "RegionStates",
    "RegionCountries",
    "URBAN_LAYER_FACTORY",
    "UrbanLayerFactory",
    "AdminFeatures",
    "AdminRegions",
    "CustomUrbanLayer",
]
