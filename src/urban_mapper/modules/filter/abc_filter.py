from abc import ABC, abstractmethod
from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.utils import require_arguments_not_none
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase


@beartype
class GeoFilterBase(ABC):
    @abstractmethod
    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame: ...

    @require_arguments_not_none(
        "input_geodataframe", error_msg="Input GeoDataFrame cannot be None."
    )
    @require_arguments_not_none("urban_layer", error_msg="Urban layer cannot be None.")
    def transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        return self._transform(input_geodataframe, urban_layer)

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        pass
