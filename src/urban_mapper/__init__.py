from loguru import logger

from .mixins import (
    LoaderMixin,
    EnricherMixin,
    VisualMixin,
    TableVisMixin,
    AuctusSearchMixin,
    PipelineGeneratorMixin,
    UrbanPipelineMixin,
    ModelMixin
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
    ModelFactory, 
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
    "ModelMixin",
    "ModelFactory", 
]
