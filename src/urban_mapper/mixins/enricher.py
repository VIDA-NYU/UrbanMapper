from urban_mapper.modules.enricher.enricher_factory import EnricherFactory


class EnricherMixin(EnricherFactory):
    """
    Mixin providing access to data enrichment functionality through the UrbanMapper interface.

    This class extends EnricherFactory to provide seamless integration of data enrichment
    capabilities within the UrbanMapper ecosystem. It enables users to enrich geospatial
    data with additional attributes through various aggregation strategies.

    The mixin pattern allows UrbanMapper to compose enrichment functionality alongside
    other components while maintaining a unified, intuitive API for users.

    Inherits all methods from EnricherFactory, including:
        - single_aggregator(): Enrich data using a single aggregation strategy
        - custom(): Create custom enrichment configurations
        - preview(): Preview available enrichment options

    Example:
        >>> mapper = UrbanMapper()
        >>> # Load some point data
        >>> restaurants = mapper.loader.from_csv('restaurants.csv')
        >>> # Enrich with nearby OSM features
        >>> enriched = mapper.enricher.single_aggregator(
        ...     data=restaurants,
        ...     urban_layer='osm_features',
        ...     aggregator='count'
        ... )

    See Also:
        EnricherFactory: The underlying factory class providing enricher implementations
        EnricherBase: Abstract base class for all enrichers
        BaseAggregator: Abstract base class for aggregation strategies
    """

    def __init__(self):
        super().__init__()
