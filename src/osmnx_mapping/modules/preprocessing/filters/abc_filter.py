from abc import ABC, abstractmethod
import geopandas as gpd
from beartype import beartype
from osmnx_mapping.utils import require_arguments_not_none


class GeoFilterBase(ABC):
    @abstractmethod
    @beartype
    def _transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame: ...

    @require_arguments_not_none(
        "input_geodataframe", error_msg="Input GeoDataFrame cannot be None."
    )
    @beartype
    def transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return self._transform(input_geodataframe)
