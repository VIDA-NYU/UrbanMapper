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
    """Loader for `Parquet` files containing spatial data.

    This loader reads data from `Parquet` files and converts them to `GeoDataFrames`
    with point geometries. It requires latitude and longitude columns to create
    point geometries for each row.

    Attributes:
        file_path (Union[str, Path]): Path to the Parquet file to load.
        latitude_column (Optional[str]): Name of the column containing latitude values. Default: `None`
        longitude_column (Optional[str]): Name of the column containing longitude values. Default: `None`
        coordinate_reference_system (str): The coordinate reference system to use. Default: `EPSG:4326`
        engine (str): The engine to use for reading Parquet files. Default: `"pyarrow"`
        columns (Optional[list[str]]): List of columns to read from the Parquet file. Default: `None`, which reads all columns.

    Examples:
        >>> from urban_mapper.modules.loader import ParquetLoader
        >>>
        >>> # Basic usage
        >>> loader = ParquetLoader(
        ...     file_path="data.parquet",
        ...     latitude_column="lat",
        ...     longitude_column="lon"
        ... )
        >>> gdf = loader.load_data_from_file()
        >>>
        >>> # With custom columns and engine
        >>> loader = ParquetLoader(
        ...     file_path="data.parquet",
        ...     latitude_column="latitude",
        ...     longitude_column="longitude",
        ...     engine="fastparquet",
        ...     columns=["latitude", "longitude", "value"]
        ... )
        >>> gdf = loader.load_data_from_file()
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        engine: str = "pyarrow",
        columns: Optional[list[str]] = None,
        **additional_loader_parameters: Any,
    ) -> None:
        super().__init__(
            file_path=file_path,
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            coordinate_reference_system=coordinate_reference_system,
            **additional_loader_parameters,
        )
        self.engine = engine
        self.columns = columns

    @require_attributes(["latitude_column", "longitude_column"])
    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        """Load data from a `Parquet` file and convert it to a `GeoDataFrame`.

        This method reads a `Parquet` file using `pandas`, validates the latitude and
        longitude columns, and converts the data to a `GeoDataFrame` with point
        geometries using the specified coordinate reference system.

        Returns:
            A `GeoDataFrame` containing the loaded data with point geometries
            created from the latitude and longitude columns.

        Raises:
            ValueError: If `latitude_column` or `longitude_column` is `None`.
            ValueError: If the specified latitude or longitude columns are not found in the Parquet file.
            IOError: If the Parquet file cannot be read.
        """
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
        """Generate a preview of this `Parquet` loader.

        Creates a summary representation of the loader for quick inspection.

        Args:
            format: The output format for the preview. Options include:

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use

        Returns:
            A string or dictionary representing the loader, depending on the format.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        cols = self.columns if self.columns else "All columns"

        if format == "ascii":
            return (
                f"Loader: ParquetLoader\n"
                f"  File: {self.file_path}\n"
                f"  Latitude Column: {self.latitude_column}\n"
                f"  Longitude Column: {self.longitude_column}\n"
                f"  Engine: {self.engine}\n"
                f"  Columns: {cols}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Additional params: {self.additional_loader_parameters}\n"
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
                "additional_params": self.additional_loader_parameters,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
