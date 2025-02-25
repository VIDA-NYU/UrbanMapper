import pandas as pd
import geopandas as gpd
from beartype import beartype
from pathlib import Path
from typing import Union, Optional

from osmnx_mapping.modules.loader.abc_loader import LoaderBase
from osmnx_mapping.config import DEFAULT_CRS
from osmnx_mapping.utils import require_attributes


@beartype
class ParquetLoader(LoaderBase):
    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column_name: Optional[str] = None,
        longitude_column_name: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        engine: str = "pyarrow",
        columns: Optional[list[str]] = None,
    ) -> None:
        super().__init__(
            file_path=file_path,
            latitude_column_name=latitude_column_name,
            longitude_column_name=longitude_column_name,
            coordinate_reference_system=coordinate_reference_system,
        )
        self.engine = engine
        self.columns = columns

    @require_attributes(["latitude_column_name", "longitude_column_name"])
    def _load_data(self) -> gpd.GeoDataFrame:
        dataframe = pd.read_parquet(
            self.file_path,
            engine=self.engine,
            columns=self.columns,
        )

        if self.latitude_column_name not in dataframe.columns:
            raise ValueError(
                f"Column '{self.latitude_column_name}' not found in the Parquet file."
            )
        if self.longitude_column_name not in dataframe.columns:
            raise ValueError(
                f"Column '{self.longitude_column_name}' not found in the Parquet file."
            )

        dataframe[self.latitude_column_name] = pd.to_numeric(
            dataframe[self.latitude_column_name], errors="coerce"
        )
        dataframe[self.longitude_column_name] = pd.to_numeric(
            dataframe[self.longitude_column_name], errors="coerce"
        )

        geodataframe = gpd.GeoDataFrame(
            dataframe,
            geometry=gpd.points_from_xy(
                dataframe[self.longitude_column_name],
                dataframe[self.latitude_column_name],
            ),
            crs=self.coordinate_reference_system,
        )
        return geodataframe
