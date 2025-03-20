import json
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import geopandas as gpd
from beartype import beartype

from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.modules.loader.loaders.csv_loader import CSVLoader
from urban_mapper.modules.loader.loaders.shapefile_loader import ShapefileLoader
from urban_mapper.modules.loader.loaders.parquet_loader import ParquetLoader
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes
from urban_mapper.utils.helpers.reset_attribute_before import reset_attributes_before
from urban_mapper import logger

FILE_LOADER_FACTORY = {
    ".csv": {"class": CSVLoader, "requires_columns": True},
    ".shp": {"class": ShapefileLoader, "requires_columns": False},
    ".parquet": {"class": ParquetLoader, "requires_columns": True},
}


@beartype
class LoaderFactory:
    def __init__(self):
        self.source_type: Optional[str] = None
        self.source_data: Optional[Union[str, pd.DataFrame, gpd.GeoDataFrame]] = None
        self.latitude_column: Optional[str] = None
        self.longitude_column: Optional[str] = None
        self.crs: str = DEFAULT_CRS
        self._instance: Optional[LoaderBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(
        ["source_type", "source_data", "latitude_column", "longitude_column"]
    )
    def from_file(self, file_path: str) -> "LoaderFactory":
        self.source_type = "file"
        self.latitude_column = None
        self.longitude_column = None
        self.source_data = file_path
        logger.log(
            "DEBUG_LOW",
            f"FROM_FILE: Initialised LoaderFactory with file_path={file_path}",
        )
        return self

    def from_dataframe(
        self, dataframe: Union[pd.DataFrame, gpd.GeoDataFrame]
    ) -> "LoaderFactory":
        self.source_type = "dataframe"
        self.source_data = dataframe
        self.latitude_column = "None"
        self.longitude_column = "None"
        logger.log(
            "DEBUG_LOW",
            f"FROM_DATAFRAME: Initialised LoaderFactory with dataframe={dataframe}",
        )
        return self

    def with_columns(
        self,
        longitude_column: str,
        latitude_column: str,
    ) -> "LoaderFactory":
        self.latitude_column = latitude_column
        self.longitude_column = longitude_column
        logger.log(
            "DEBUG_LOW",
            f"WITH_COLUMNS: Initialised LoaderFactory "
            f"with latitude_column={latitude_column} and longitude_column={longitude_column}",
        )
        return self

    def with_crs(self, crs: str = DEFAULT_CRS) -> "LoaderFactory":
        self.crs = crs
        logger.log(
            "DEBUG_LOW",
            f"WITH_CRS: Initialised LoaderFactory with crs={crs}",
        )
        return self

    def _load_from_file(self, coordinate_reference_system: str) -> gpd.GeoDataFrame:
        file_path: str = self.source_data
        file_ext = Path(file_path).suffix.lower()
        loader_class = FILE_LOADER_FACTORY[file_ext]["class"]
        self._instance = loader_class(
            file_path,
            latitude_column=self.latitude_column,
            longitude_column=self.longitude_column,
            coordinate_reference_system=coordinate_reference_system,
        )
        return self._instance.load_data_from_file()

    def _load_from_dataframe(
        self, coordinate_reference_system: str
    ) -> gpd.GeoDataFrame:
        input_dataframe: Union[pd.DataFrame, gpd.GeoDataFrame] = self.source_data
        if isinstance(input_dataframe, gpd.GeoDataFrame):
            geo_dataframe: gpd.GeoDataFrame = input_dataframe.copy()
        else:
            geo_dataframe = gpd.GeoDataFrame(
                input_dataframe,
                geometry=gpd.points_from_xy(
                    input_dataframe[self.longitude_column],
                    input_dataframe[self.latitude_column],
                ),
                crs=coordinate_reference_system,
            )
        if geo_dataframe.crs is None:
            geo_dataframe.set_crs(coordinate_reference_system, inplace=True)
        elif geo_dataframe.crs.to_string() != coordinate_reference_system:
            geo_dataframe = geo_dataframe.to_crs(coordinate_reference_system)
        return geo_dataframe

    @require_attributes(["source_type", "source_data"])
    def load(self, coordinate_reference_system: str = DEFAULT_CRS) -> gpd.GeoDataFrame:
        if self.source_type == "file":
            file_ext = Path(self.source_data).suffix.lower()
            if file_ext not in FILE_LOADER_FACTORY:
                raise ValueError(f"Unsupported file format: {file_ext}")
            loader_info = FILE_LOADER_FACTORY[file_ext]
            if loader_info["requires_columns"] and (
                self.latitude_column is None or self.longitude_column is None
            ):
                raise ValueError(
                    f"Loader for {file_ext} requires latitude and longitude columns. Call with_columns() first."
                )
            loaded_data = self._load_from_file(coordinate_reference_system)
            if self._preview is not None:
                self.preview(format=self._preview["format"])
            return loaded_data
        elif self.source_type == "dataframe":
            if self.latitude_column == "None" or self.longitude_column == "None":
                raise ValueError(
                    "DataFrame loading requires latitude and longitude columns. Call with_columns() with valid column names."
                )
            loaded_data = self._load_from_dataframe(coordinate_reference_system)
            if self._preview is not None:
                logger.log(
                    "DEBUG_LOW",
                    "Note: Preview is not supported for DataFrame sources.",
                )
            return loaded_data
        else:
            raise ValueError("Invalid source type.")

    def build(self) -> LoaderBase:
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. "
            "In other cases, using .load() is a better option.",
        )
        if self.source_type != "file":
            raise ValueError("Build only supports file sources for now.")
        file_ext = Path(self.source_data).suffix.lower()
        if file_ext not in FILE_LOADER_FACTORY:
            raise ValueError(f"Unsupported file format: {file_ext}")
        loader_info = FILE_LOADER_FACTORY[file_ext]
        loader_class = loader_info["class"]
        requires_columns = loader_info["requires_columns"]
        if requires_columns and (
            self.latitude_column is None or self.longitude_column is None
        ):
            raise ValueError(
                f"Loader for {file_ext} requires latitude and longitude columns. Call with_columns() first."
            )
        self._instance = loader_class(
            file_path=self.source_data,
            latitude_column=self.latitude_column,
            longitude_column=self.longitude_column,
            coordinate_reference_system=self.crs,
        )
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format="ascii") -> None:
        if self._instance is None:
            logger.log(
                "DEBUG_LOW",
                "No loader instance available to preview. Call load() first.",
            )
            return

        if hasattr(self._instance, "preview"):
            preview_data = self._instance.preview(format=format)
            if format == "ascii":
                print(preview_data)
            elif format == "json":
                print(json.dumps(preview_data, indent=2))
            else:
                raise ValueError(f"Unsupported format '{format}'.")
        else:
            logger.log("DEBUG_LOW", "Preview not supported for this loader's instance.")

    def with_preview(self, format="ascii") -> "LoaderFactory":
        self._preview = {
            "format": format,
        }
        return self
