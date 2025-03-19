from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.filter.abc_filter import GeoFilterBase


@beartype
class BoundingBoxFilter(GeoFilterBase):
    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        if not hasattr(urban_layer, "get_layer_bounding_box"):
            raise AttributeError(
                f"Urban layer {urban_layer.__class__.__name__} does not have a method to get its bounding box."
            )
        minx, miny, maxx, maxy = urban_layer.get_layer_bounding_box()
        return input_geodataframe.cx[minx:maxx, miny:maxy]

    def preview(self, format: str = "ascii") -> Any:
        if format == "ascii":
            return (
                "Filter: BoundingBoxFilter\n"
                "  Action: Filter data to the bounding box of the urban layer"
            )
        elif format == "json":
            return {
                "filter": "BoundingBoxFilter",
                "action": "Filter data to the bounding box of the urban layer",
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
