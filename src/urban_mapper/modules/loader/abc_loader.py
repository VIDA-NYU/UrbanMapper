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
    def _load_data_from_file(self) -> gpd.GeoDataFrame: ...

    @file_exists("file_path")
    @ensure_coordinate_reference_system
    def load_data_from_file(self) -> gpd.GeoDataFrame:
        return self._load_data_from_file()

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        pass
