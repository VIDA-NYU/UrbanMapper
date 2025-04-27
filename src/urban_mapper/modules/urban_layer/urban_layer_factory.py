from beartype import beartype
from typing import Type, Dict, Tuple, List, Optional
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.utils.helpers import require_attributes_not_none
from urban_mapper import logger
from thefuzz import process
import json


@beartype
class UrbanLayerFactory:
    """Factory for creating `urban layer` instances with a fluent chaining-method-based interface.

        This factory class provides a `chainable API` for creating and configuring
        `urban layer` instances. It supports setting the `layer type`, `loading method`,
        `mappings`, and `preview` options before `building` the final `urban layer` instance.

        The factory uses method chaining for a fluent, expressive API:

            - [x] Set the layer type with `with_type()`
            - [x] Set the loading method with `from_*()` methods
            - [x] Add mappings with `with_mapping()`
            - [x] Build the layer instance with `build()`

        !!! tip "What are the various type available?"
            The available types are defined in the `URBAN_LAYER_FACTORY` dictionary.
            As follows:

            - [x] `streets_roads`: OSMNXStreets
            - [x] `streets_intersections`: OSMNXIntersections
            - [x] `streets_sidewalks`: Tile2NetSidewalks
            - [x] `streets_crosswalks`: Tile2NetCrosswalks
            - [x] `streets_features`: OSMFeatures
            - [x] `region_cities`: RegionCities
            - [x] `region_neighborhoods`: RegionNeighborhoods
            - [x] `region_states`: RegionStates
            - [x] `region_countries`: RegionCountries
            - [x] `custom_urban_layer`: CustomUrbanLayer

        Attributes:
            layer_class: The class of the `urban layer` to create.
            loading_method: The method to call to load the `urban layer`.
            loading_args: Positional arguments for the loading method.
            loading_kwargs: Keyword arguments for the loading method.
            mappings: List of mapping configurations for this layer.

        Examples:
            >>> from urban_mapper as um
            >>> streets = um.UrbanMapper().urban_layer\
            ...     .with_type("streets_roads")\
            ...     .from_place("Manhattan, New York")\
            ...     .with_mapping(
            ...         longitude_column="pickup_lng",
            ...         latitude_column="pickup_lat",
            ...         output_column="nearest_street"
            ...     )\
            ...     .with_preview("ascii")\
            ...     .build()
        """

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
        """Set the type of `urban layer` to create.

        Args:
            primitive_type: String identifier for the `urban layer` type.
                Must be one of the registered layer types in `URBAN_LAYER_FACTORY`.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If the provided type is not registered in `URBAN_LAYER_FACTORY`.
                Includes a suggestion if a similar type is available.

        Examples:
            >>> factory = UrbanLayerFactory().with_type("streets_roads")
        """
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
        """Add a mapping configuration to the `urban layer`.

        Mappings define how the `urban layer` should be joined or related to other data.
        Each mapping specifies which columns contain the coordinates to map, and
        what the output column should be named.

        Args:
            longitude_column: Name of the column containing longitude values in the data
                to be mapped to this `urban layer`.
            latitude_column: Name of the column containing latitude values in the data
                to be mapped to this `urban layer`.
            output_column: Name of the column that will contain the mapping results.
                Must be unique across all mappings for this layer.
            **mapping_kwargs: Additional parameters specific to the mapping operation.
                Common parameters include `threshold_distance`, `max_distance`, etc.

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If the `output_column` is already used in another mapping.

        Examples:
            >>> factory = um.UrbanMapper().urban_layer\
            ...     .with_type("streets_roads")\
            ...     .from_place("Manhattan, New York")\
            ...     .with_mapping(
            ...         longitude_column="pickup_lng",
            ...         latitude_column="pickup_lat",
            ...         output_column="nearest_street",
            ...         threshold_distance=100
            ...     )
        """
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
        """Build and return the configured `urban layer` instance.

        This method creates an instance of the specified `urban layer` class,
        calls the loading method with the specified arguments, and attaches
        any mappings that were added.

        Returns:
            An initialised `urban layer` instance of the specified type,
            loaded with the specified data and configured with the specified mappings.

        Raises:
            ValueError: If `layer_class` or `loading_method` is not set, or if the
                loading method is not available for the specified layer class.

        Examples:
            >>> streets = um.UrbanMapper().urban_layer\
            ...     .with_type("osmnx_streets")\
            ...     .from_place("Manhattan, New York")\
            ...     .with_mapping(
            ...         longitude_column="pickup_lng",
            ...         latitude_column="pickup_lat",
            ...         output_column="nearest_street"
            ...     )\
            ...     .build()
        """
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
        """Display a preview of the built `urban layer`.

        This method generates and displays a preview of the `urban layer` instance
        that was created by the `build()` method.

        Args:
            format: The output format for the preview ("ascii" or "json").

        Raises:
            ValueError: If an unsupported format is requested.

        Examples:
            >>> streets = um.UrbanMapper().urban_layer\
            ...     .with_type("osmnx_streets")\
            ...     .from_place("Manhattan, New York")\
            ...     .build()
            >>> streets.preview()
        """
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
        """Enable automatic preview after building the `urban layer`.

        This method sets up the factory to automatically display a preview
        of the `urban layer` instance after it is built with `build()`.

        Args:
            format: The output format for the preview ("ascii" or "json").

        Returns:
            Self, for method chaining.

        Examples:
            >>> streets = UrbanLayerFactory()\
            ...     .with_type("osmnx_streets")\
            ...     .from_place("Manhattan, New York")\
            ...     .with_preview("json")\
            ...     .build()
        """
        self._preview = {"format": format}
        return self
