from pathlib import Path
from typing import Union, Optional, Any, Tuple
from beartype import beartype
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.modules.loader.abc_loader import LoaderBase


@beartype
class FileLoaderBase(LoaderBase):
    """FileLoaderBase For `Loaders`.

    This abstract class defines the common interface that all loader implementations
    **must implement**. `Loaders` are responsible for reading spatial data from various
    file formats and converting them to `GeoDataFrames` data structure. They handle coordinate system
    transformations and validation of required spatial columns.

    Attributes:
        file_path (Path): Path to the file to load.
        latitude_column (str): Name of the column containing latitude values.
        longitude_column (str): Name of the column containing longitude values.
        coordinate_reference_system (Union[str, Tuple[str, str]]):
            If a string, it specifies the coordinate reference system to use (default: 'EPSG:4326').
            If a tuple (source_crs, target_crs), it defines a conversion from the source CRS to the target CRS (default target CRS: 'EPSG:4326').
        additional_loader_parameters (Dict[str, Any]): Additional parameters specific to the loader implementation. Consider this as `kwargs`.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        geometry_column: Optional[str] = None,
        coordinate_reference_system: Union[str, Tuple[str, str]] = DEFAULT_CRS,
        **additional_loader_parameters: Any,
    ) -> None:
        super().__init__(
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            geometry_column=geometry_column,
            coordinate_reference_system=coordinate_reference_system,
            **additional_loader_parameters,
        )
        self.file_path: Path = Path(file_path)
