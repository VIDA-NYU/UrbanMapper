from abc import ABC, abstractmethod
from typing import Optional, Any
import geopandas as gpd
from beartype import beartype

from urban_mapper.utils import require_arguments_not_none, require_attributes
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase


@beartype
class GeoImputerBase(ABC):
    def __init__(
        self,
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
    ) -> None:
        self.latitude_column = latitude_column
        self.longitude_column = longitude_column

    @abstractmethod
    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame: ...

    @require_arguments_not_none(
        "input_geodataframe", error_msg="Input GeoDataFrame cannot be None."
    )
    @require_arguments_not_none("urban_layer", error_msg="Urban layer cannot be None.")
    @require_attributes(["latitude_column", "longitude_column"])
    def transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        return self._transform(input_geodataframe, urban_layer)

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        pass
