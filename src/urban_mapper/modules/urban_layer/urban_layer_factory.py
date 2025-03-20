from beartype import beartype
from typing import Type, Dict, Tuple, List, Optional
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.utils.helpers import require_attributes_not_none
from urban_mapper import logger
from thefuzz import process
import json


@beartype
class UrbanLayerFactory:
    def __init__(self):
        self.layer_class: Type[UrbanLayerBase] | None = None
        self.loading_method: str | None = None
        self.loading_args: Tuple[object, ...] = ()
        self.loading_kwargs: Dict[str, object] = {}
        self.mappings: List[Dict[str, object]] = []
        self._layer_recently_reset: bool = False
        self._instance: Optional[UrbanLayerBase] = None
        self._preview: Optional[dict] = None

    def with_type(self, primitive_type: str) -> "UrbanLayerFactory":
        if self.layer_class is not None:
            logger.log(
                "DEBUG_MID",
                f"Attribute 'layer_class' is being overwritten from {self.layer_class} to None. "
                f"Prior to most probably being set again by the method you are calling.",
            )
            self.layer_class = None
            self._layer_recently_reset = True
        if self.loading_method is not None:
            logger.log(
                "DEBUG_MID",
                f"Attribute 'loading_method' is being overwritten from {self.loading_method} to None. "
                f"Prior to most probably being set again by the method you are calling.",
            )
            self.loading_method = None

        from urban_mapper.modules.urban_layer import URBAN_LAYER_FACTORY

        if primitive_type not in URBAN_LAYER_FACTORY:
            available = list(URBAN_LAYER_FACTORY.keys())
            match, score = process.extractOne(primitive_type, available)
            if score > 80:
                suggestion = f" Maybe you meant '{match}'?"
            else:
                suggestion = ""
            raise ValueError(
                f"Unsupported layer type: {primitive_type}. Supported types: {', '.join(available)}.{suggestion}"
            )
        self.layer_class = URBAN_LAYER_FACTORY[primitive_type]
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised UrbanLayerFactory with layer_class={self.layer_class}",
        )
        return self

    def with_mapping(
        self,
        longitude_column: str | None = None,
        latitude_column: str | None = None,
        output_column: str | None = None,
        **mapping_kwargs,
    ) -> "UrbanLayerFactory":
        if self._layer_recently_reset:
            logger.log(
                "DEBUG_MID",
                f"Attribute 'mappings' is being overwritten from {self.mappings} to []. "
                f"Prior to most probably being set again by the method you are calling.",
            )
            self.mappings = []
            self._layer_recently_reset = False

        if output_column in [m.get("output_column") for m in self.mappings]:
            raise ValueError(
                f"Output column '{output_column}' is already used in another mapping."
            )

        mapping = {}
        if longitude_column:
            mapping["longitude_column"] = longitude_column
        if latitude_column:
            mapping["latitude_column"] = latitude_column
        if output_column:
            mapping["output_column"] = output_column
        mapping["kwargs"] = mapping_kwargs

        self.mappings.append(mapping)
        logger.log(
            "DEBUG_LOW",
            f"WITH_MAPPING: Added mapping with output_column={output_column}",
        )
        return self

    def __getattr__(self, name: str):
        if name.startswith("from_"):

            def wrapper(*args, **kwargs):
                self.loading_method = name
                self.loading_args = args
                self.loading_kwargs = kwargs
                logger.log(
                    "DEBUG_LOW",
                    f"{name}: Initialised UrbanLayerFactory with args={args} and kwargs={kwargs}",
                )
                return self

            return wrapper
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    @require_attributes_not_none(
        "layer_class",
        error_msg="Layer type must be set using with_type() before building.",
    )
    @require_attributes_not_none(
        "loading_method",
        error_msg="A loading method must be specified before building the layer.",
    )
    def build(self) -> UrbanLayerBase:
        layer = self.layer_class()
        if not hasattr(layer, self.loading_method):
            raise ValueError(
                f"'{self.loading_method}' is not available for {self.layer_class.__name__}"
            )
        loading_func = getattr(layer, self.loading_method)
        loading_func(*self.loading_args, **self.loading_kwargs)
        layer.mappings = self.mappings
        self._instance = layer
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return layer

    def preview(self, format: str = "ascii") -> None:
        if self._instance is None:
            print("No urban layer instance available to preview. Call build() first.")
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
            print("Preview not supported for this urban layer instance.")

    def with_preview(self, format: str = "ascii") -> "UrbanLayerFactory":
        self._preview = {"format": format}
        return self
