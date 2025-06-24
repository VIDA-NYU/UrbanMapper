from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Optional, Any, Dict
import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.loader.helpers import ensure_coordinate_reference_system
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import file_exists


@beartype
class LoaderBase(ABC):
    """Base Class For `Loaders`.

    This abstract class defines the common interface that all loader implementations
    **must implement**. `Loaders` are responsible for reading spatial data from various
    file formats and converting them to `GeoDataFrames` data structure. They handle coordinate system
    transformations and validation of required spatial columns.

    Attributes:
        file_path (Path): Path to the file to load.
        latitude_column (str): Name of the column containing latitude values.
        longitude_column (str): Name of the column containing longitude values.
        coordinate_reference_system (str): The coordinate reference system to use. Default: `EPSG:4326`.
        additional_loader_parameters (Dict[str, Any]): Additional parameters specific to the loader implementation. Consider this as `kwargs`.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        **additional_loader_parameters: Any,
    ) -> None:
        self.file_path: Path = Path(file_path)
        self.latitude_column: str = latitude_column or ""
        self.longitude_column: str = longitude_column or ""
        self.coordinate_reference_system: str = coordinate_reference_system
        self.additional_loader_parameters: Dict[str, Any] = additional_loader_parameters

    @abstractmethod
    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        """Internal implementation method for loading data from a file.

        This method is called by `load_data_from_file()` after validation is performed.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for reading the file and converting it to a `GeoDataFrame`.

        Returns:
            A `GeoDataFrame` containing the loaded spatial data.

        Raises:
            ValueError: If required columns are missing or the file format is invalid.
            FileNotFoundError: If the file does not exist.
        """
        ...

    @file_exists("file_path")
    @ensure_coordinate_reference_system
    def load_data_from_file(self) -> gpd.GeoDataFrame:
        """Load spatial data from a file.

        This is the main public method for using `loaders`. It performs validation
        on the inputs before delegating to the implementation-specific `_load_data_from_file` method.
        It also ensures the file exists and that the coordinate reference system is properly set.

        Returns:
            A `GeoDataFrame` containing the loaded spatial data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If required columns are missing or the file format is invalid.

        Examples:
            >>> from urban_mapper.modules.loader import CSVLoader
            >>> loader = CSVLoader("taxi_data.csv", latitude_column="pickup_lat", longitude_column="pickup_lng")
            >>> gdf = loader.load_data_from_file()
        """
        loaded_file = self._load_data_from_file()

        if self.additional_loader_parameters.get("map_columns") is not None:
            loaded_file = loaded_file.rename(
                columns=self.additional_loader_parameters["map_columns"]
            )

        return loaded_file

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of the instance's `loader`.

        Creates a summary representation of the loader for quick inspection during UrbanMapper's analysis workflow.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should provide a preview
            of the loader's configuration and data. Make sure to support all formats.

        Args:
            format: The output format for the preview. Options include:

                - [x] `ascii`: Text-based format for terminal display
                - [x] `json`: JSON-formatted data for programmatic use

        Returns:
            A representation of the `loader` in the requested format.
            Return type varies based on the format parameter.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        pass
