from abc import ABC, abstractmethod
from typing import Any, List, Dict
import geopandas as gpd
from urban_mapper.utils.helpers import require_dynamic_columns


class VisualiserBase(ABC):
    def __init__(self, style: Dict[str, Any] = None):
        self.style = style or {}

    @abstractmethod
    def _render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        pass

    @require_dynamic_columns("urban_layer_geodataframe", lambda args: args["columns"])
    def render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        if "geometry" not in urban_layer_geodataframe.columns:
            raise ValueError("GeoDataFrame must have a 'geometry' column.")
        if urban_layer_geodataframe.empty:
            raise ValueError("GeoDataFrame is empty; nothing to visualise.")
        return self._render(urban_layer_geodataframe, columns, **kwargs)

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        pass
