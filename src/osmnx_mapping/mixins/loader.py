from pathlib import Path
from typing import Optional, Type, Union
import geopandas as gpd
import pandas as pd
from beartype import beartype
from osmnx_mapping.modules.loader.loaders.csv_loader import CSVLoader
from osmnx_mapping.modules.loader.loaders.shapefile_loader import ShapefileLoader
from osmnx_mapping.modules.loader.loaders.dummy_loader import DummyLoader
from osmnx_mapping.modules.loader.loaders.parquet_loader import (
    ParquetLoader,
)
from osmnx_mapping.config import DEFAULT_CRS

FILE_LOADER_FACTORY: dict[str, Type] = {
    ".csv": CSVLoader,
    ".shp": ShapefileLoader,
    ".parquet": ParquetLoader,
}


@beartype
class LoaderMixin:
    def __init__(self, coordinate_reference_system: str = DEFAULT_CRS) -> None:
        self.data: Optional[gpd.GeoDataFrame] = None
        self.latitude_column_name: str = ""
        self.longitude_column_name: str = ""
        self.coordinate_reference_system: str = coordinate_reference_system

    @beartype
    def load_from_file(
        self, file_path: str, latitude_column: str = "", longitude_column: str = ""
    ) -> gpd.GeoDataFrame:
        file_path_obj = Path(file_path)
        file_ext = file_path_obj.suffix.lower()
        if file_ext not in FILE_LOADER_FACTORY:
            raise ValueError(
                f"Unsupported file format: {file_ext}. Supported formats: {list(FILE_LOADER_FACTORY.keys())}"
            )
        loader_class = FILE_LOADER_FACTORY[file_ext]
        loader_instance = loader_class(
            file_path_obj,
            latitude_column,
            longitude_column,
            self.coordinate_reference_system,
        )
        loaded_dataset = loader_instance.load_data_from_file()

        self.latitude_column_name = loader_instance.latitude_column_name
        self.longitude_column_name = loader_instance.longitude_column_name

        if len(self.latitude_column_name) == 0 or len(self.longitude_column_name) == 0:
            raise ValueError(
                "Error: Latitude and Longitude does not seems to have been provided/created following "
                f"the application of the {loader_instance.__class__.__name__} loader."
            )

        if loaded_dataset.crs is None:
            loaded_dataset.set_crs(self.coordinate_reference_system, inplace=True)
        elif loaded_dataset.crs.to_string() != self.coordinate_reference_system:
            loaded_dataset = loaded_dataset.to_crs(self.coordinate_reference_system)

        self.data = loaded_dataset
        return self.data

    @beartype
    def load_from_dataframe(
        self,
        input_dataframe: Union[pd.DataFrame, gpd.GeoDataFrame],
        latitude_column: str,
        longitude_column: str,
    ) -> gpd.GeoDataFrame:
        loader_instance = DummyLoader(
            "dummy.csv",
            latitude_column,
            longitude_column,
            self.coordinate_reference_system,
        )
        loaded_dataset = loader_instance.load_data_from_dataframe(
            input_dataframe, latitude_column, longitude_column
        )

        self.latitude_column_name = loader_instance.latitude_column_name
        self.longitude_column_name = loader_instance.longitude_column_name
        self.data = loaded_dataset
        return self.data
