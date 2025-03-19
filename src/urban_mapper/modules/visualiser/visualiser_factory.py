import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import geopandas as gpd
from beartype import beartype
from .abc_visualiser import VisualiserBase
from ...utils.helpers.reset_attribute_before import reset_attributes_before
from urban_mapper import logger
from thefuzz import process
import json

VISUALISER_REGISTRY = {}


@beartype
class VisualiserFactory:
    def __init__(self):
        self._type = None
        self._style = {}
        self._columns = None
        self._instance: Optional[VisualiserBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(["_type", "_style", "_columns"])
    def with_type(self, primitive_type: str):
        if primitive_type not in VISUALISER_REGISTRY:
            available = list(VISUALISER_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            if score > 80:
                suggestion = f" Maybe you meant '{match}'?"
            else:
                suggestion = ""
            raise ValueError(
                f"Unknown visualiser type '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self._type = primitive_type
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised VisualiserFactory with type={primitive_type}",
        )
        return self

    @reset_attributes_before(["_style"])
    def with_style(self, style: Dict[str, Any]):
        self._style.update(style)
        logger.log(
            "DEBUG_LOW", f"WITH_STYLE: Initialised VisualiserFactory with style={style}"
        )
        return self

    def show(self, columns: Union[str, List[str]]):
        if isinstance(columns, str):
            columns = [columns]
        self._columns = columns
        logger.log(
            "DEBUG_LOW",
            f"SHOW: Initialised VisualiserFactory while displaying columns={columns}",
        )
        return self

    def render(self, urban_layer_geodataframe: gpd.GeoDataFrame):
        if self._type is None:
            raise ValueError("Visualiser type must be specified.")
        if self._columns is None:
            raise ValueError("Columns to visualize must be specified.")

        visualiser_class = VISUALISER_REGISTRY[self._type]
        allowed_keys = visualiser_class.allowed_style_keys
        invalid_keys = set(self._style.keys()) - allowed_keys
        if invalid_keys:
            allowed = ", ".join(sorted(allowed_keys))
            raise ValueError(
                f"Invalid style keys for {self._type}: {invalid_keys}. Allowed keys: {allowed}"
            )

        self._instance = visualiser_class()
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance.render(
            urban_layer_geodataframe, self._columns, **self._style
        )

    def build(self) -> VisualiserBase:
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. "
            "In other cases, using render() is a better option.",
        )
        if self._type is None:
            raise ValueError("Visualiser type must be specified.")
        visualiser_class = VISUALISER_REGISTRY[self._type]
        self._instance = visualiser_class(style=self._style)
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format: str = "ascii") -> None:
        if self._instance is None:
            print("No visualiser instance available to preview. Call build() first.")
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
            print("Preview not supported for this visualiser instance.")

    def with_preview(self, format: str = "ascii") -> "VisualiserFactory":
        self._preview = {"format": format}
        return self


@beartype
def register_visualiser(name: str, visualiser_class: type):
    if not issubclass(visualiser_class, VisualiserBase):
        raise TypeError(f"{visualiser_class.__name__} must subclass VisualiserBase")
    VISUALISER_REGISTRY[name] = visualiser_class


def _initialise():
    package_dir = Path(__file__).parent / "visualisers"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(
                f".visualisers.{module_name}", package=__package__
            )
            for class_name, class_object in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(class_object, VisualiserBase)
                    and class_object is not VisualiserBase
                    and hasattr(class_object, "short_name")
                ):
                    short_name = class_object.short_name
                    if short_name in VISUALISER_REGISTRY:
                        raise ValueError(
                            f"Duplicate short_name '{short_name}' in visualiser registry."
                        )
                    register_visualiser(short_name, class_object)
        except ImportError as error:
            raise ImportError(
                f"Failed to load visualisers module {module_name}: {error}"
            )


_initialise()
