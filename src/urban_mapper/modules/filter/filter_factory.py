from typing import Optional, Dict, Any, Type
import importlib
import inspect
import pkgutil
from pathlib import Path
from beartype import beartype
import geopandas as gpd
import json
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.utils.helpers import require_attributes_not_none
from .abc_filter import GeoFilterBase
from ...utils.helpers.reset_attribute_before import reset_attributes_before
from urban_mapper import logger
from thefuzz import process

FILTER_REGISTRY: Dict[str, Type[GeoFilterBase]] = {}


@beartype
def register_filter(name: str, filter_class: Type[GeoFilterBase]) -> None:
    if not issubclass(filter_class, GeoFilterBase):
        raise TypeError(f"{filter_class} must be a subclass of GeoFilterBase")
    FILTER_REGISTRY[name] = filter_class


@beartype
class FilterFactory:
    def __init__(self):
        self._filter_type: Optional[str] = None
        self._config: Dict[str, Any] = {}
        self._instance: Optional[GeoFilterBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(["_filter_type"])
    def with_type(self, primitive_type: str) -> "FilterFactory":
        if self._filter_type is not None:
            logger.log(
                "DEBUG_MID",
                f"WARNING: Filter method already set to '{self._filter_type}'. Overwriting.",
            )
            self._filter_type = None
        if primitive_type not in FILTER_REGISTRY:
            available = list(FILTER_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            if score > 80:
                suggestion = f" Maybe you meant '{match}'?"
            else:
                suggestion = ""
            raise ValueError(
                f"Unknown filter method '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self._filter_type = primitive_type
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised FilterFactory with filter_type={primitive_type}",
        )
        return self

    @require_attributes_not_none("_filter_type")
    def transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        filter_class = FILTER_REGISTRY[self._filter_type]
        self._instance = filter_class(**self._config)
        return self._instance.transform(input_geodataframe, urban_layer)

    def build(self) -> GeoFilterBase:
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. In other cases, "
            "using transform() is a better choice.",
        )
        if self._filter_type is None:
            raise ValueError("Filter type must be specified. Call with_type() first.")
        filter_class = FILTER_REGISTRY[self._filter_type]
        self._instance = filter_class(**self._config)
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format: str = "ascii") -> None:
        if self._instance is None:
            print("No filter instance available to preview. Call build() first.")
            return
        if hasattr(self._instance, "preview"):
            preview_data = self._instance.preview(format=format)
            if format == "ascii":
                print(preview_data)
            elif format == "json":
                print(json.dumps(preview_data, indent=2))
            else:
                raise ValueError(f"Unsupported format '{format}'.")
        else:
            print("Preview not supported for this filter instance.")

    def with_preview(self, format: str = "ascii") -> "FilterFactory":
        self._preview = {"format": format}
        return self


def _initialise():
    package_dir = Path(__file__).parent / "filters"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(
                f".filters.{module_name}", package=__package__
            )
            for class_name, class_object in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(class_object, GeoFilterBase)
                    and class_object is not GeoFilterBase
                ):
                    register_filter(class_name, class_object)
        except ImportError as error:
            raise ImportError(f"Failed to load filters module {module_name}: {error}")


_initialise()
