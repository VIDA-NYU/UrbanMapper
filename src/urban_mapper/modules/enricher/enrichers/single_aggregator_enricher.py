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
    """Enricher Using a `Single Aggregator` For `Urban Layers`.

    Uses one aggregator to enrich `urban layers`, adding `results as a new column`.
    The aggregator decides how input data is processed (e.g., `counted`, `averaged`).

    Attributes:
        config: Config object for the enricher.
        aggregator: Aggregator computing stats or counts.
        output_column: Column name for aggregated results.
        debug: Whether to include debug info.

    Examples:
        >>> import urban_mapper as um
        >>> mapper = um.UrbanMapper()
        >>> streets = mapper.urban_layer.OSMNXStreets().from_place("London, UK")
        >>> trips = mapper.loader.from_file("trips.csv")\
        ...     .with_columns(longitude_column="lng", latitude_column="lat")\
        ...     .load()
        >>> enricher = mapper.enricher\
        ...     .with_data(group_by="nearest_street")\
        ...     .count_by(output_column="trip_count")\
        ...     .build()
        >>> enriched_streets = enricher.enrich(trips, streets)
    """

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
        """Enrich an `urban layer` with an `aggregator`.

        Aggregates data from the input `GeoDataFrame` and adds it to the urban layer.

        Args:
            input_geodataframe: `GeoDataFrame` with enrichment data.
            urban_layer: Urban layer to enrich.
            **kwargs: Extra params for customisation.

        Returns:
            Enriched urban layer with new columns.

        Raises:
            ValueError: If aggregation fails.
        """
        aggregated_df = self.aggregator.aggregate(input_geodataframe)
        enriched_values = (
            aggregated_df["value"].reindex(urban_layer.layer.index).fillna(0)
        )
        urban_layer = self.set_layer_data_source(urban_layer, aggregated_df.index)
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
        """Generate a preview of this enricher.

        Creates a summary for quick inspection.

        Args:
            format: Output format—"ascii" (text) or "json" (dict).

        Returns:
            Preview in the requested format.
        """
        preview_builder = PreviewBuilder(self.config, ENRICHER_REGISTRY)
        return preview_builder.build_preview(format=format)
