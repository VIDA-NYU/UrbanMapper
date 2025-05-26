from beartype import beartype
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.config.container import container
from urban_mapper.utils import LazyMixin
import sys
from loguru import logger


class UrbanMapper:
    """
    Main interface for the UrbanMapper geospatial analysis library.

    This class provides a unified entry point for accessing all UrbanMapper functionality
    through dynamic mixins, including data loading, enrichment, visualization, and pipeline
    generation. The class uses a lazy loading pattern to instantiate mixins only when accessed.

    The UrbanMapper class automatically configures logging levels and coordinate reference
    systems, and provides seamless access to all library components through attribute access.

    Attributes:
        coordinate_reference_system (str): The CRS used for all geospatial operations.
        loader (LoaderMixin): Access to data loading functionality.
        enricher (EnricherMixin): Access to data enrichment tools.
        visualiser (VisualMixin): Access to visualization capabilities.
        pipeline_generator (PipelineGeneratorMixin): Access to AI-powered pipeline generation.
        auctus (AuctusSearchMixin): Access to external data discovery.
        table_vis (TableVisMixin): Access to interactive table visualization.
        urban_pipeline (UrbanPipelineMixin): Access to pipeline execution.

    Example:
        Basic usage with default settings:

        >>> mapper = UrbanMapper()
        >>> data = mapper.loader.from_csv('restaurants.csv')
        >>> enriched = mapper.enricher.single_aggregator(data, 'osm_features')
        >>> mapper.visualiser.interactive(enriched)

        With custom CRS and debug logging:

        >>> mapper = UrbanMapper(
        ...     coordinate_reference_system='EPSG:3857',
        ...     debug='HIGH'
        ... )
        >>> # All operations will use Web Mercator projection
        >>> # and show detailed debug information

    Note:
        Mixins are instantiated lazily - they are only created when first accessed.
        This improves startup performance and memory usage.
    """
    @beartype
    def __init__(
        self, coordinate_reference_system: str = DEFAULT_CRS, debug: str = None
    ):
        """
        Initialize the UrbanMapper with configuration settings.

        Args:
            coordinate_reference_system: The coordinate reference system to use
                for all geospatial operations. Defaults to EPSG:4326 (WGS84).
                Common alternatives include EPSG:3857 (Web Mercator) for web
                mapping applications.
            debug: Debug logging level. Options are:
                - None: Only critical messages (default)
                - 'LOW': Basic debug information with 🔍 icon
                - 'MID': Moderate debug information with ☂️ icon  
                - 'HIGH': Detailed debug information with 🔬 icon

        Raises:
            ValueError: If debug level is not None, 'LOW', 'MID', or 'HIGH'.

        Example:
            >>> # Default configuration
            >>> mapper = UrbanMapper()
            >>> 
            >>> # Custom CRS for projected coordinates
            >>> mapper = UrbanMapper(coordinate_reference_system='EPSG:3857')
            >>>
            >>> # Enable debug logging
            >>> mapper = UrbanMapper(debug='MID')
        """
        self.coordinate_reference_system = coordinate_reference_system
        self._instances = {}
        self._mixin_classes = container.mixin_classes()

        logger.remove()

        if debug is None:
            logger.add(
                sys.stderr,
                level="CRITICAL",
                format="<green>{time:YYYY-MM-DD HH:mm}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True,
            )
        else:
            debug_levels = {
                "LOW": "DEBUG_LOW",
                "MID": "DEBUG_MID",
                "HIGH": "DEBUG_HIGH",
            }
            if debug not in debug_levels:
                raise ValueError(
                    f"Invalid debug level: {debug}. Choose from {list(debug_levels.keys())} or None"
                )
            logger.add(
                sys.stderr,
                level=debug_levels[debug],
                format="<green>{time:YYYY-MM-DD HH:mm}</green> | {level.icon} <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True,
            )

    def __getattr__(self, name):
        """
        Dynamically access mixin functionality through attribute access.

        This method implements lazy loading of mixins - they are only instantiated
        when first accessed. Subsequent accesses return the cached instance.

        Args:
            name: The name of the mixin to access. Available mixins include:
                - loader: Data loading functionality (LoaderMixin)
                - enricher: Data enrichment tools (EnricherMixin)
                - visualiser: Visualization capabilities (VisualMixin)
                - pipeline_generator: AI pipeline generation (PipelineGeneratorMixin)
                - auctus: External data discovery (AuctusSearchMixin)
                - table_vis: Interactive tables (TableVisMixin)
                - urban_pipeline: Pipeline execution (UrbanPipelineMixin)

        Returns:
            LazyMixin: A proxy object that provides access to the mixin functionality.

        Raises:
            AttributeError: If the requested mixin name is not configured in the
                system. Check config.yaml for available mixins.

        Example:
            >>> mapper = UrbanMapper()
            >>> # First access creates the mixin
            >>> loader = mapper.loader
            >>> # Subsequent accesses return the same instance
            >>> same_loader = mapper.loader
            >>> assert loader is same_loader
        """
        if name in self._mixin_classes:
            if name in self._instances:
                return self._instances[name]
            proxy = LazyMixin(self, name, self._mixin_classes[name])
            self._instances[name] = proxy
            return proxy
        raise AttributeError(
            f"UrbanMapper has no mixin '{name}', maybe update the config yaml file?"
        )
