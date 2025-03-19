import pandas as pd
import geopandas as gpd
from beartype import beartype
from pathlib import Path
from typing import Union, Optional, Any

from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes


@beartype
class ParquetLoader(LoaderBase):
    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        engine: str = "pyarrow",
        columns: Optional[list[str]] = None,
    ) -> None:
        super().__init__(
            file_path=file_path,
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            coordinate_reference_system=coordinate_reference_system,
        )
        self.engine = engine
        self.columns = columns

    @require_attributes(["latitude_column", "longitude_column"])
    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        dataframe = pd.read_parquet(
            self.file_path,
            engine=self.engine,
            columns=self.columns,
        )

        if self.latitude_column not in dataframe.columns:
            raise ValueError(
                f"Column '{self.latitude_column}' not found in the Parquet file."
            )
        if self.longitude_column not in dataframe.columns:
            raise ValueError(
                f"Column '{self.longitude_column}' not found in the Parquet file."
            )

        dataframe[self.latitude_column] = pd.to_numeric(
            dataframe[self.latitude_column], errors="coerce"
        )
        dataframe[self.longitude_column] = pd.to_numeric(
            dataframe[self.longitude_column], errors="coerce"
        )

        geodataframe = gpd.GeoDataFrame(
            dataframe,
            geometry=gpd.points_from_xy(
                dataframe[self.longitude_column],
                dataframe[self.latitude_column],
            ),
            crs=self.coordinate_reference_system,
        )
        return geodataframe

    def preview(self, format: str = "ascii") -> Any:
        cols = self.columns if self.columns else "All columns"

        if format == "ascii":
            return (
                f"Loader: ParquetLoader\n"
                f"  File: {self.file_path}\n"
                f"  Latitude Column: {self.latitude_column}\n"
                f"  Longitude Column: {self.longitude_column}\n"
                f"  Engine: {self.engine}\n"
                f"  Columns: {cols}\n"
                f"  CRS: {self.coordinate_reference_system}"
            )
        elif format == "json":
            return {
                "loader": "ParquetLoader",
                "file": self.file_path,
                "latitude_column": self.latitude_column,
                "longitude_column": self.longitude_column,
                "engine": self.engine,
                "columns": cols,
                "coordinate_reference_system": self.coordinate_reference_system,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
