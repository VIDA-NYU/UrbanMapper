from abc import ABC, abstractmethod
from typing import Optional
import geopandas as gpd
from beartype import beartype

from osmnx_mapping.utils import require_arguments_not_none, require_attributes


class GeoImputerBase(ABC):
    @beartype
    def __init__(
        self,
        latitude_column_name: Optional[str] = None,
        longitude_column_name: Optional[str] = None,
    ) -> None:
        self.latitude_column_name = latitude_column_name
        self.longitude_column_name = longitude_column_name

    @abstractmethod
    def _transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame: ...

    @require_arguments_not_none(
        "input_geodataframe", error_msg="Input GeoDataFrame cannot be None."
    )
    @require_attributes(["latitude_column_name", "longitude_column_name"])
    @beartype
    def transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return self._transform(input_geodataframe)
