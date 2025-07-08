from abc import ABC, abstractmethod
from typing import Optional, Any, Union, Dict
import geopandas as gpd, pandas as pd, numpy as np
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from pandas.core.indexes.base import Index


@beartype
class EnricherBase(ABC):
    """Base class for all data enrichers in `UrbanMapper`

    This abstract class defines the common interface that all enricher implementations
    must implement. Enrichers add data or derived information to urban layers,
    enhancing them with additional attributes, statistics, or related data.

    !!! note "Enrichers typically perform operations like:"

        - [x] Aggregating data values (sum, mean, median, etc.)
        - [x] Counting features within areas or near points
        - [x] Computing statistics on related data
        - [x] Joining external information to the urban layer

    Attributes:
        config: Configuration object for the enricher, containing parameters
            that control the enrichment process.
    """

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
        """Internal method to carry out the enrichment.

        This method must be fleshed out by subclasses to define the nitty-gritty
        of how enrichment happens.

        !!! warning "Method Not Implemented"
            Subclasses must implement this. It’s where the logic of enrichment takes place.

        Args:
            input_geodataframe: The GeoDataFrame with data for enrichment.
            urban_layer: The urban layer to be enriched.
            **kwargs: Extra parameters to tweak the enrichment.

        Returns:
            The enriched urban layer.
        """
        NotImplementedError("_enrich method not implemented.")

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of the enricher instance.

        Produces a summary of the enricher for a quick peek during `UrbanMapper`’s workflow.

        !!! warning "Method Not Implemented"
            Subclasses must implement this to offer a preview of the enricher’s setup and data.

        Args:
            format: Output format for the preview. Options include:

                - [x] `ascii`: Text-based format for terminal display
                - [x] `json`: JSON-formatted data for programmatic use

        Returns:
            A representation of the enricher in the requested format. Type varies by format.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        NotImplementedError("Preview method not implemented.")

    def set_layer_data_source(
        self, urban_layer: UrbanLayerBase, index: Index
    ) -> UrbanLayerBase:
        """Initialized UrbanLayer data_id column with source name based on index list argument.

        Args:
            urban_layer: Urban layer to change.
            index: Index list of the Urban layer to change.

        Returns:
            Urban layer with new column data_id.
        """
        if self.config.data_id:
            if "data_id" not in urban_layer.layer:
                urban_layer.layer["data_id"] = pd.Series(np.nan, dtype="object")

            urban_layer.layer.loc[index, "data_id"] = self.config.data_id

        return urban_layer

    def enrich(
        self,
        input_geodataframe: Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame],
        urban_layer: UrbanLayerBase,
        **kwargs,
    ) -> UrbanLayerBase:
        """Enrich an `urban layer` with data from the input `GeoDataFrame`.

        The main public method for wielding enrichers. It hands off to the
        implementation-specific `_enrich` method after any needed validation.

        Args:
            input_geodataframe: one or more `GeoDataFrame` with data to enrich with.
            urban_layer: Urban layer to beef up with data from input_geodataframe.
            **kwargs: Additional bespoke parameters to customise enrichment.

        Returns:
            The enriched urban layer sporting new columns or attributes.

        Raises:
            ValueError: If the enrichment can’t be done.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> streets = mapper.urban_layer.OSMNXStreets().from_place("London, UK")
            >>> taxi_trips = mapper.loader.from_file("taxi_trips.csv")\
            ...     .with_columns(longitude_column="pickup_lng", latitude_column="pickup_lat")\
            ...     .load()
            >>> enricher = mapper.enricher\
            ...     .with_type("SingleAggregatorEnricher")\
            ...     .with_data(group_by="nearest_street")\
            ...     .count_by(output_column="trip_count")\
            ...     .build()
            >>> enriched_streets = enricher.enrich(taxi_trips, streets)
        """
        if isinstance(input_geodataframe, gpd.GeoDataFrame):
            return self._enrich(input_geodataframe, urban_layer, **kwargs)
        else:
            enriched_layer = urban_layer

            for key, gdf in input_geodataframe.items():
                if self.config.data_id is None or self.config.data_id == key:
                    enriched_layer = self._enrich(gdf, enriched_layer, **kwargs)

            return enriched_layer
