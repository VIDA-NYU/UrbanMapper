from typing import Optional, Dict, Any, Type, Union
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
    """Factory class for creating and configuring spatial filters

    Provides a fluent chaining-based-methods interface to instantiate `filters`, `configure settings`, and `apply` them
    to `GeoDataFrames`.

    Attributes:
        _filter_type (Optional[str]): The type of filter to create.
        _extra_params (Dict[str, Any]): Configuration parameters for the filter.
        _instance (Optional[GeoFilterBase]): The filter instance (internal use).
        _preview (Optional[dict]): Preview configuration (internal use).

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> import geopandas as gpd
        >>> mapper = UrbanMapper()
        >>> layer = mapper.urban_layer.region_neighborhoods().from_place("Brooklyn, New York")
        >>> data = gpd.read_file("nyc_points.csv") # Example data
        >>> filtered_data = mapper.filter.with_type("BoundingBoxFilter")\
        ...     .transform(data, layer)
    """

    def __init__(self):
        self._filter_type: Optional[str] = None
        self._extra_params: Dict[str, Any] = {}
        self._instance: Optional[GeoFilterBase] = None
        self._preview: Optional[dict] = None
        self._data_id: Optional[str] = None

    @reset_attributes_before(["_filter_type"])
    def with_type(self, primitive_type: str) -> "FilterFactory":
        """Specify the type of filter to use.

        Configures the factory to create a specific filter type from FILTER_REGISTRY.

        !!! tip "FILTER_REGISTRY looks like this"
            Open the folder `filters` in `src/urban_mapper/modules/filter` to see the available filter types
            in FILTER_REGISTRY. Each filter class is registered under its class name.

            You also can use `list(FILTER_REGISTRY.keys())` to see available filter types.

        Args:
            primitive_type (str): The name of the filter type (e.g., "BoundingBoxFilter").

        Returns:
            FilterFactory: Self for method chaining.

        Raises:
            ValueError: If primitive_type is not in FILTER_REGISTRY.

        Examples:
            >>> filter_factory = mapper.filter.with_type("BoundingBoxFilter")

        """
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

    def with_data(self, data_id: str) -> "FilterFactory":
        """Set the data ID to perform filtering.

        Args:
            data_id: ID of the dataset to be transformed

        Returns:
            FilterFactory: Self for chaining.

        Raises:
            ValueError: If primitive_type is not in FILTER_REGISTRY.

        !!! tip
            Check FILTER_REGISTRY keys for valid filtering types.
        """
        if self._data_id is not None:
            logger.log(
                "DEBUG_MID",
                f"WARNING: Data ID already set to '{self._data_id}'. Overwriting.",
            )
            self._data_id = None

        self._data_id = data_id
        logger.log(
            "DEBUG_LOW",
            f"WITH_DATA: Initialised FilterFactory with data_id={data_id}",
        )
        return self

    @require_attributes_not_none("_filter_type")
    def transform(
        self,
        input_geodataframe: Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame],
        urban_layer: UrbanLayerBase,
    ) -> Union[
        Dict[str, gpd.GeoDataFrame],
        gpd.GeoDataFrame,
    ]:
        """Apply the filter to input data and return filtered results

        Creates and applies a filter instance to the input `GeoDataFrame`.

        Args:
            input_geodataframe (Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame]): one or more `GeoDataFrame` to filter.
            urban_layer (UrbanLayerBase): The urban layer for filtering criteria.

        Returns:
            Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame]: The filtered data.

        Raises:
            ValueError: If _filter_type is not set.

        Examples:
            >>> layer = mapper.urban_layer.region_neighborhoods().from_place("Brooklyn, New York")
            >>> data = gpd.read_file("nyc_points.csv") # Example data
            >>> filtered_data = mapper.filter.with_type("BoundingBoxFilter")\
            ...     .transform(data, layer)
        """
        filter_class = FILTER_REGISTRY[self._filter_type]
        self._instance = filter_class(data_id=self._data_id, **self._extra_params)

        if (
            isinstance(input_geodataframe, Dict)
            and self._data_id is not None
            and self._data_id not in input_geodataframe
        ):
            print(
                "WARNING: ",
                f"Data ID {self._data_id} was not found in the list of dataframes ",
                "No filter transformation will be executed ",
            )

        return self._instance.transform(input_geodataframe, urban_layer)

    def build(self) -> GeoFilterBase:
        """Build and return a filter instance without applying it.

        Creates a filter instance for use in pipelines or deferred execution.

        !!! note
            Prefer `transform()` for immediate filtering; use build() for pipelines.

        Returns:
            GeoFilterBase: A configured filter instance.

        Raises:
            ValueError: If _filter_type is not set.

        Examples:
            >>> filter_component = mapper.filter.with_type("BoundingBoxFilter").build()
            >>> pipeline.add_filter(filter_component)
        """
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. In other cases, "
            "using transform() is a better choice.",
        )
        if self._filter_type is None:
            raise ValueError("Filter type must be specified. Call with_type() first.")
        filter_class = FILTER_REGISTRY[self._filter_type]
        self._instance = filter_class(
            data_id=self._data_id,
            **self._extra_params,
        )
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format: str = "ascii") -> None:
        """Display a preview of the filter configuration and settings.

        Shows the filter’s configuration in the specified format.

        !!! note
            Requires a prior call to build() or transform().

        Args:
            format (str): The format to display ("ascii" or "json"). Defaults to "ascii".

        Raises:
            ValueError: If format is unsupported.

        Examples:
            >>> factory = mapper.filter.with_type("BoundingBoxFilter")
            >>> factory.build()
            >>> factory.preview(format="json")
        """
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
        """Configure the factory to display a preview after building.

        Enables automatic preview after build().

        Args:
            format (str): The preview format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            FilterFactory: Self for chaining.

        Examples:
            >>> filter_component = mapper.filter.with_type("BoundingBoxFilter")\
            ...     .with_preview(format="json")\
            ...     .build()
        """
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


# Initialise the filter registry when the module is imported
_initialise()
