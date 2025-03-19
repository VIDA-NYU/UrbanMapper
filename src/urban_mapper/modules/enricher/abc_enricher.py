from abc import ABC, abstractmethod
from typing import Optional, Any
import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase


@beartype
class EnricherBase(ABC):
    def __init__(self, config: Optional[Any] = None) -> None:
        from urban_mapper.modules.enricher.factory.config import EnricherConfig

        self.config = config or EnricherConfig()

    @abstractmethod
    def _enrich(
        self,
        input_geodataframe: gpd.GeoDataFrame,
        urban_layer: UrbanLayerBase,
        **kwargs,
    ) -> UrbanLayerBase:
        NotImplementedError("_enrich method not implemented.")

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        NotImplementedError("Preview method not implemented.")

    def enrich(
        self,
        input_geodataframe: gpd.GeoDataFrame,
        urban_layer: UrbanLayerBase,
        **kwargs,
    ) -> UrbanLayerBase:
        return self._enrich(input_geodataframe, urban_layer, **kwargs)
