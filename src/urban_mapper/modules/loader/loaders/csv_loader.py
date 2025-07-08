import pandas as pd
import geopandas as gpd
from beartype import beartype
from pathlib import Path
from typing import Union, Optional, Any

from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes


@beartype
class CSVLoader(LoaderBase):
    """Loader for `CSV` files containing spatial data.

    This loader reads data from `CSV` (or other delimiter-separated) files and
    converts them to `GeoDataFrames` with point geometries. It requires latitude
    and longitude columns to create point geometries for each row.

    Attributes:
        file_path (Path): Path to the `CSV` file to load.
        latitude_column (str): Name of the column containing latitude values.
        longitude_column (str): Name of the column containing longitude values.
        coordinate_reference_system (str): The coordinate reference system to use. Default: `EPSG:4326`
        separator (str): The delimiter character used in the CSV file. Default: `","`
        encoding (str): The character encoding of the CSV file. Default: `"utf-8"`

    Examples:
        >>> from urban_mapper.modules.loader import CSVLoader
        >>>
        >>> # Basic usage
        >>> loader = CSVLoader(
        ...     file_path="taxi_trips.csv",
        ...     latitude_column="pickup_lat",
        ...     longitude_column="pickup_lng"
        ... )
        >>> gdf = loader.load_data_from_file()
        >>>
        >>> # With custom separator and encoding
        >>> loader = CSVLoader(
        ...     file_path="custom_data.csv",
        ...     latitude_column="lat",
        ...     longitude_column="lng",
        ...     separator=";",
        ...     encoding="latin-1"
        ... )
        >>> gdf = loader.load_data_from_file()
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        separator: str = ",",
        encoding: str = "utf-8",
        **additional_loader_parameters: Any,
    ) -> None:
        super().__init__(
            file_path=file_path,
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            coordinate_reference_system=coordinate_reference_system,
            **additional_loader_parameters,
        )
        self.separator = separator
        self.encoding = encoding

    @require_attributes(["latitude_column", "longitude_column"])
    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        """Load data from a CSV file and convert it to a `GeoDataFrame`.

        This method reads a `CSV` file using pandas, validates the latitude and
        longitude columns, and converts the data to a `GeoDataFrame` with point
        geometries using the specified coordinate reference system.

        Returns:
            A `GeoDataFrame` containing the loaded data with point geometries
            created from the latitude and longitude columns.

        Raises:
            ValueError: If latitude_column or longitude_column is None.
            ValueError: If the specified columns are not found in the CSV file.
            pd.errors.ParserError: If the CSV file cannot be parsed.
            UnicodeDecodeError: If the file encoding is incorrect.
        """
        dataframe = pd.read_csv(
            self.file_path, sep=self.separator, encoding=self.encoding
        )

        if self.latitude_column not in dataframe.columns:
            raise ValueError(
                f"Column '{self.latitude_column}' not found in the CSV file."
            )
        if self.longitude_column not in dataframe.columns:
            raise ValueError(
                f"Column '{self.longitude_column}' not found in the CSV file."
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
        """Generate a preview of this `CSV` loader.

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
        if format == "ascii":
            return (
                f"Loader: CSVLoader\n"
                f"  File: {self.file_path}\n"
                f"  Latitude Column: {self.latitude_column}\n"
                f"  Longitude Column: {self.longitude_column}\n"
                f"  Separator: {self.separator}\n"
                f"  Encoding: {self.encoding}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Additional params: {self.additional_loader_parameters}\n"
            )
        elif format == "json":
            return {
                "loader": "CSVLoader",
                "file": self.file_path,
                "latitude_column": self.latitude_column,
                "longitude_column": self.longitude_column,
                "separator": self.separator,
                "encoding": self.encoding,
                "crs": self.coordinate_reference_system,
                "additional_params": self.additional_loader_parameters,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
