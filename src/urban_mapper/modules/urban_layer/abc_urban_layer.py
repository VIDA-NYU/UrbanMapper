from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
import geopandas as gpd
from beartype import beartype
from pathlib import Path
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes_not_none
from urban_mapper import logger


@beartype
class UrbanLayerBase(ABC):
    def __init__(self) -> None:
        self.layer: gpd.GeoDataFrame | None = None
        self.mappings: List[Dict[str, object]] = []
        self.coordinate_reference_system: str = DEFAULT_CRS
        self.has_mapped: bool = False

    @abstractmethod
    def from_place(self, place_name: str, **kwargs) -> None:
        pass

    @abstractmethod
    def from_file(self, file_path: str | Path, **kwargs) -> None:
        pass

    @abstractmethod
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_element",
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        pass

    @abstractmethod
    def get_layer(self) -> gpd.GeoDataFrame:
        pass

    @abstractmethod
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        pass

    @abstractmethod
    def static_render(self, **plot_kwargs) -> None:
        pass

    @require_attributes_not_none(
        "layer",
        error_msg="Urban layer not built. Please call from_place() or from_file() first.",
    )
    def map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str | None = None,
        latitude_column: str | None = None,
        output_column: str | None = None,
        threshold_distance: float | None = None,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        if self.has_mapped:
            raise ValueError(
                "This layer has already been mapped. If you want to map again, create a new instance."
            )
        if longitude_column or latitude_column or output_column:
            if not (longitude_column and latitude_column and output_column):
                raise ValueError(
                    "When overriding mappings, longitude_column, latitude_column, and output_column "
                    "must all be specified."
                )
            mapping_kwargs = (
                {"threshold_distance": threshold_distance} if threshold_distance else {}
            )
            mapping_kwargs.update(kwargs)
            result = self._map_nearest_layer(
                data,
                longitude_column,
                latitude_column,
                output_column,
                **mapping_kwargs,
            )
            self.has_mapped = True
            return result

        if not self.mappings:
            raise ValueError(
                "No mappings defined. Use with_mapping() during layer creation."
            )

        mapped_data = data.copy()
        for mapping in self.mappings:
            lon_col = mapping.get("longitude_column", None)
            lat_col = mapping.get("latitude_column", None)
            out_col = mapping.get("output_column", None)
            if not (lon_col and lat_col and out_col):
                raise ValueError(
                    "Each mapping must specify longitude_column, latitude_column, and output_column."
                )

            mapping_kwargs = mapping.get("kwargs", {}).copy()
            if threshold_distance is not None:
                mapping_kwargs["threshold_distance"] = threshold_distance
            mapping_kwargs.update(kwargs)

            if None in [lon_col, lat_col, out_col]:
                raise ValueError(
                    "All of longitude_column, latitude_column, and output_column must be specified."
                )
            if self.mappings[-1]:
                logger.log(
                    "DEBUG_MID",
                    "INFO: Last mapping, resetting urban layer's index.",
                )
            self.layer, temp_mapped = self._map_nearest_layer(
                mapped_data,
                lon_col,
                lat_col,
                out_col,
                _reset_layer_index=(True if mapping == self.mappings[-1] else False),
                **mapping_kwargs,
            )
            mapped_data[out_col] = temp_mapped[out_col]

        self.has_mapped = True
        return self.layer, mapped_data

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        pass
