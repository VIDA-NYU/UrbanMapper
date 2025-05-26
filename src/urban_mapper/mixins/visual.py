from urban_mapper.modules.visualiser import VisualiserFactory


class VisualMixin(VisualiserFactory):
    """
    Mixin providing access to visualization functionality through the UrbanMapper interface.

    This class extends VisualiserFactory to provide seamless integration of visualization
    capabilities within the UrbanMapper ecosystem. It enables users to create both
    interactive and static visualizations of their geospatial data.

    The mixin pattern allows UrbanMapper to compose visualization functionality alongside
    other components while maintaining a clean, unified API for creating maps and charts.

    Inherits all methods from VisualiserFactory, including:
        - interactive(): Create interactive maps with folium
        - static(): Create static maps with matplotlib
        - preview(): Preview available visualization options

    Example:
        >>> mapper = UrbanMapper()
        >>> # Load and enrich some data
        >>> data = mapper.loader.from_csv('restaurants.csv')
        >>> enriched = mapper.enricher.single_aggregator(data, 'osm_features')
        >>> # Create an interactive visualization
        >>> mapper.visualiser.interactive(enriched, color_column='osm_features_count')
        >>> # Or create a static plot
        >>> mapper.visualiser.static(enriched, figsize=(12, 8))

    See Also:
        VisualiserFactory: The underlying factory class providing visualizer implementations
        VisualiserBase: Abstract base class for all visualizers
        InteractiveVisualiser: Interactive mapping with folium
        StaticVisualiser: Static plotting with matplotlib
    """

    def __init__(self):
        super().__init__()
