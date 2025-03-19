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
from .abc_imputer import GeoImputerBase
from ...utils.helpers.reset_attribute_before import reset_attributes_before
from urban_mapper import logger
from thefuzz import process

IMPUTER_REGISTRY: Dict[str, Type[GeoImputerBase]] = {}


@beartype
def register_imputer(name: str, imputer_class: Type[GeoImputerBase]) -> None:
    if not issubclass(imputer_class, GeoImputerBase):
        raise TypeError(f"{imputer_class} must be a subclass of GeoImputerBase")
    IMPUTER_REGISTRY[name] = imputer_class


@beartype
class ImputerFactory:
    def __init__(self):
        self._imputer_type: Optional[str] = None
        self._latitude_column: Optional[str] = None
        self._longitude_column: Optional[str] = None
        self._config: Dict[str, Any] = {}
        self._instance: Optional[GeoImputerBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(["_imputer_type", "_latitude_column", "_longitude_column"])
    def with_type(self, primitive_type: str) -> "ImputerFactory":
        if self._imputer_type is not None:
            logger.log(
                "DEBUG_MID",
                f"WARNING: Imputer method already set to '{self._imputer_type}'. Overwriting.",
            )
            self._imputer_type = None

        if primitive_type not in IMPUTER_REGISTRY:
            available = list(IMPUTER_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            if score > 80:
                suggestion = f" Maybe you meant '{match}'?"
            else:
                suggestion = ""
            raise ValueError(
                f"Unknown imputer method '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self._imputer_type = primitive_type
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised ImputerFactory with imputer_type={primitive_type}",
        )
        return self

    def on_columns(
        self, longitude_column: str, latitude_column: str
    ) -> "ImputerFactory":
        self._longitude_column = longitude_column
        self._latitude_column = latitude_column
        logger.log(
            "DEBUG_LOW",
            f"ON_COLUMNS: Initialised ImputerFactory with "
            f"longitude_column={longitude_column}, latitude_column={latitude_column}",
        )
        return self

    @require_attributes_not_none(
        "_imputer_type",
        "_latitude_column",
        "_longitude_column",
    )
    def transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        imputer_class = IMPUTER_REGISTRY[self._imputer_type]
        self._instance = imputer_class(
            latitude_column=self._latitude_column,
            longitude_column=self._longitude_column,
            **self._config,
        )
        return self._instance.transform(input_geodataframe, urban_layer)

    def build(self) -> GeoImputerBase:
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. In other cases, "
            "using transform() is a better choice.",
        )
        if self._imputer_type is None:
            raise ValueError("Imputer type must be specified. Call with_type() first.")
        if self._latitude_column is None or self._longitude_column is None:
            raise ValueError(
                "Latitude and longitude columns must be specified. Call on_columns() first."
            )
        imputer_class = IMPUTER_REGISTRY[self._imputer_type]
        self._instance = imputer_class(
            latitude_column=self._latitude_column,
            longitude_column=self._longitude_column,
            **self._config,
        )
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format: str = "ascii") -> None:
        if self._instance is None:
            print("No imputer instance available to preview. Call build() first.")
            return
        if hasattr(self._instance, "preview"):
            preview_data = self._instance.preview(format=format)
            if format == "ascii":
                print(preview_data)
            elif format == "json":
                print(json.dumps(preview_data, indent=2))
            else:
                raise ValueError(f"Unsupported format '{format}'")
        else:
            print("Preview not supported for this imputer instance.")

    def with_preview(self, format: str = "ascii") -> "ImputerFactory":
        self._preview = {"format": format}
        return self


def _initialise():
    package_dir = Path(__file__).parent / "imputers"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(
                f".imputers.{module_name}", package=__package__
            )
            for class_name, class_object in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(class_object, GeoImputerBase)
                    and class_object is not GeoImputerBase
                ):
                    register_imputer(class_name, class_object)
        except ImportError as error:
            raise ImportError(f"Failed to load imputers module {module_name}: {error}")


_initialise()
