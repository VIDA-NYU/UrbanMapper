from typing import Any

import geopandas as gpd
from beartype import beartype

from urban_mapper.modules.enricher.factory import PreviewBuilder, ENRICHER_REGISTRY
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.enricher.abc_enricher import EnricherBase
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator
from urban_mapper.modules.enricher.factory.config import EnricherConfig


@beartype
class SingleAggregatorEnricher(EnricherBase):
    def __init__(
        self,
        aggregator: BaseAggregator,
        output_column: str = "aggregated_value",
        config: EnricherConfig = None,
    ) -> None:
        super().__init__(config)
        self.aggregator = aggregator
        self.output_column = output_column

    def _enrich(
        self,
        input_geodataframe: gpd.GeoDataFrame,
        urban_layer: UrbanLayerBase,
        **kwargs,
    ) -> UrbanLayerBase:
        aggregated_series = self.aggregator.aggregate(input_geodataframe)
        urban_layer.layer[self.output_column] = urban_layer.layer.index.map(
            aggregated_series
        ).fillna(0)
        return urban_layer

    def preview(self, format: str = "ascii") -> Any:
        preview_builder = PreviewBuilder(self.config, ENRICHER_REGISTRY)
        return preview_builder.build_preview(format=format)
