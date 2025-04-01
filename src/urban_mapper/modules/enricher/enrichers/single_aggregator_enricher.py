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
        self.debug = config.debug

    def _enrich(
        self,
        input_geodataframe: gpd.GeoDataFrame,
        urban_layer: UrbanLayerBase,
        **kwargs,
    ) -> UrbanLayerBase:
        aggregated_df = self.aggregator.aggregate(input_geodataframe)
        enriched_values = (
            aggregated_df["value"].reindex(urban_layer.layer.index).fillna(0)
        )
        urban_layer.layer[self.output_column] = enriched_values
        if self.debug:
            indices_values = (
                aggregated_df["indices"]
                .reindex(urban_layer.layer.index)
                .apply(lambda x: x if isinstance(x, list) else [])
            )
            urban_layer.layer[f"DEBUG_{self.output_column}"] = indices_values
        return urban_layer

    def preview(self, format: str = "ascii") -> Any:
        preview_builder = PreviewBuilder(self.config, ENRICHER_REGISTRY)
        return preview_builder.build_preview(format=format)
