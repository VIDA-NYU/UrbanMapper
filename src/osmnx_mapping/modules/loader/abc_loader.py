from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Optional, Any, Dict
import geopandas as gpd
import pandas as pd
from beartype import beartype
from osmnx_mapping.modules.loader.helpers import (
    ensure_coordinate_reference_system,
)
from osmnx_mapping.config import DEFAULT_CRS
from osmnx_mapping.utils import (
    file_exists,
    require_dynamic_columns,
    require_arguments_not_none,
)


@beartype
class LoaderBase(ABC):
    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column_name: Optional[str] = None,
        longitude_column_name: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        **additional_loader_parameters: Any,
    ) -> None:
        self.file_path: Path = Path(file_path)
        self.latitude_column_name: str = latitude_column_name or ""
        self.longitude_column_name: str = longitude_column_name or ""
        self.coordinate_reference_system: str = coordinate_reference_system
        self.additional_loader_parameters: Dict[str, Any] = additional_loader_parameters

    @abstractmethod
    def _load_data(self) -> gpd.GeoDataFrame: ...

    @file_exists("file_path")
    @ensure_coordinate_reference_system
    def load_data_from_file(self) -> gpd.GeoDataFrame:
        return self._load_data()

    @require_arguments_not_none(
        "input_dataframe", check_empty=True, types=(pd.DataFrame, gpd.GeoDataFrame)
    )
    @require_dynamic_columns(
        "input_dataframe",
        lambda args: [args["latitude_column_name"], args["longitude_column_name"]],
    )
    def load_data_from_dataframe(
        self,
        input_dataframe: Union[pd.DataFrame, gpd.GeoDataFrame],
        latitude_column_name: str,
        longitude_column_name: str,
    ) -> gpd.GeoDataFrame:
        if isinstance(input_dataframe, gpd.GeoDataFrame):
            geo_dataframe: gpd.GeoDataFrame = input_dataframe.copy()
        else:
            geo_dataframe = gpd.GeoDataFrame(
                input_dataframe,
                geometry=gpd.points_from_xy(
                    input_dataframe[longitude_column_name],
                    input_dataframe[latitude_column_name],
                ),
                crs=self.coordinate_reference_system,
            )
        if geo_dataframe.crs is None:
            geo_dataframe.set_crs(self.coordinate_reference_system, inplace=True)
        elif geo_dataframe.crs.to_string() != self.coordinate_reference_system:
            geo_dataframe = geo_dataframe.to_crs(self.coordinate_reference_system)
        return geo_dataframe
