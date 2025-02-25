from typing import Optional

import geopandas as gpd
from beartype import beartype
from osmnx_mapping.modules.preprocessing.filters.abc_filter import GeoFilterBase
from osmnx_mapping.utils import require_attributes_not_none


class BoundingBoxFilter(GeoFilterBase):
    @beartype
    def __init__(self, nodes: Optional[gpd.GeoDataFrame] = None) -> None:
        self.nodes = nodes

    @require_attributes_not_none(
        "nodes",
        error_msg="No nodes set while instantiating BoundingBoxFilter.",
    )
    @beartype
    def _transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        minx, miny, maxx, maxy = self.nodes.total_bounds
        return input_geodataframe.cx[minx:maxx, miny:maxy]
