"""
UrbanMapper: A comprehensive geospatial analysis library for urban data processing.

UrbanMapper provides a modular, extensible framework for loading, enriching, filtering,
and visualizing urban geospatial data. The library supports various data formats and
offers powerful tools for spatial analysis, data pipeline creation, and interactive
visualization.

Key Features:
    - Flexible data loading from CSV, Shapefile, and Parquet formats
    - Rich geospatial enrichment using OpenStreetMap and other urban layers
    - Advanced filtering and imputation capabilities
    - Interactive and static visualization tools
    - AI-powered pipeline generation
    - Modular architecture with factory patterns

Main Classes:
    UrbanMapper: Primary interface providing access to all functionality
    LoaderBase: Abstract base for data loaders
    EnricherBase: Abstract base for data enrichment
    VisualiserBase: Abstract base for visualization
    UrbanPipeline: Pipeline orchestration and execution

Example:
    >>> from urban_mapper import UrbanMapper
    >>> mapper = UrbanMapper(debug='MID')
    >>> data = mapper.loader.from_csv('restaurants.csv')
    >>> enriched = mapper.enricher.single_aggregator(data, 'osm_features')
    >>> mapper.visualiser.interactive(enriched)

See Also:
    Documentation: https://urban-mapper.readthedocs.io/
    Examples: examples/ directory in the repository
"""

from loguru import logger

from .mixins import (
    LoaderMixin,
    EnricherMixin,
    VisualMixin,
    TableVisMixin,
    AuctusSearchMixin,
    PipelineGeneratorMixin,
    UrbanPipelineMixin,
)
from .modules import (
    LoaderBase,
    CSVLoader,
    ShapefileLoader,
    ParquetLoader,
    GeoImputerBase,
    SimpleGeoImputer,
    AddressGeoImputer,
    EnricherBase,
    BaseAggregator,
    SimpleAggregator,
    SingleAggregatorEnricher,
    EnricherFactory,
    VisualiserBase,
    StaticVisualiser,
    InteractiveVisualiser,
    GPT4OPipelineGenerator,
    PipelineGeneratorBase,
    PipelineGeneratorFactory,
)

from .urban_mapper import UrbanMapper

logger.level("DEBUG_LOW", no=5, color="<blue>", icon="🔍")
logger.level("DEBUG_MID", no=10, color="<cyan>", icon="☂️")
logger.level("DEBUG_HIGH", no=15, color="<green>", icon="🔬")

__all__ = [
    "LoaderBase",
    "CSVLoader",
    "ShapefileLoader",
    "ParquetLoader",
    "GeoImputerBase",
    "SimpleGeoImputer",
    "AddressGeoImputer",
    "EnricherBase",
    "BaseAggregator",
    "SimpleAggregator",
    "SingleAggregatorEnricher",
    "EnricherFactory",
    "VisualiserBase",
    "StaticVisualiser",
    "InteractiveVisualiser",
    "LoaderMixin",
    "EnricherMixin",
    "VisualMixin",
    "TableVisMixin",
    "AuctusSearchMixin",
    "PipelineGeneratorMixin",
    "UrbanMapper",
    "GPT4OPipelineGenerator",
    "PipelineGeneratorBase",
    "PipelineGeneratorFactory",
    "UrbanPipelineMixin",
]
