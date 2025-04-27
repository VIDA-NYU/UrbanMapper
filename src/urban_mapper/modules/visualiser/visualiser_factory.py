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
    """Factory class for creating and configuring data visualisers

    Provides a fluent chaining-methods-based interface to instantiate visualisers, configure settings, and
    render visualisations within the UrbanMapper framework.

    Attributes:
        _type (Optional[str]): The type of visualiser to create.
        _style (Dict[str, Any]): Style configuration for the visualiser.
        _columns (Optional[List[str]]): Columns from the data to visualise.
        _instance (Optional[VisualiserBase]): The visualiser instance (internal use).
        _preview (Optional[dict]): Preview configuration (internal use).

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> import geopandas as gpd
        >>> mapper = UrbanMapper()
        >>> neighborhoods = mapper.urban_layer.region_neighborhoods().from_place("Manhattan, New York")
        >>> map_viz = mapper.visual.with_type("InteractiveVisualiser")\
        ...     .with_style({"width": 800, "height": 600})\
        ...     .show("neighborhood")\
        ...     .render(neighborhoods)
    """

    def __init__(self):
        self._type = None
        self._style = {}
        self._columns = None
        self._instance: Optional[VisualiserBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(["_type", "_style", "_columns"])
    def with_type(self, primitive_type: str) -> "VisualiserFactory":
        """Specify the type of visualiser to create.

        Sets the type of visualiser, determining the visualisation strategy.

        !!! question "How to find available visualiser types?"
            To find available visualiser types, you can check the `VISUALISER_REGISTRY` dictionary.
            Or directly going to the `urban_mapper.modules.visualiser.visualisers` directory.
            Each visualiser class should have a `short_name` attribute that serves as its identifier.

            Instead, you simply also can se `list(VISUALISER_REGISTRY.keys())` to see available visualiser types.

        Args:
            primitive_type (str): The name of the visualiser type (e.g., "InteractiveVisualiser").

        Returns:
            VisualiserFactory: Self for method chaining.

        Raises:
            ValueError: If primitive_type is not in VISUALISER_REGISTRY.

        Examples:
            >>> visualiser = mapper.visual.with_type("InteractiveVisualiser")

        """
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
    def with_style(self, style: Dict[str, Any]) -> "VisualiserFactory":
        """Set the style options for the visualiser.

        Configures style options like colours, width, height, and opacity.

        !!! tip "how to know which style options are available?"
            To know which style options are available, you can check the `allowed_style_keys` attribute
            in each visualiser class. This attribute contains a set of keys that are accepted for styling.

        Args:
            style (Dict[str, Any]): A dictionary of style options.

        Returns:
            VisualiserFactory: Self for method chaining.

        Examples:
            >>> visualiser = mapper.visual.with_style({
            ...     "width": 800,
            ...     "height": 600,
            ...     "color": "blue",
            ...     "opacity": 0.7
            ... })
        """
        self._style.update(style)
        logger.log(
            "DEBUG_LOW", f"WITH_STYLE: Initialised VisualiserFactory with style={style}"
        )
        return self

    def show(self, columns: Union[str, List[str]]) -> "VisualiserFactory":
        """Specify which columns from the data should be visualised.

        Sets the columns to include in the visualisation.

        Args:
            columns (Union[str, List[str]]): A single column name or list of column names.

        Returns:
            VisualiserFactory: Self for method chaining.

        Examples:
            >>> visualiser = mapper.visual.show("population")
            >>> visualiser = mapper.visual.show(["population", "area"])
        """
        if isinstance(columns, str):
            columns = [columns]
        self._columns = columns
        logger.log(
            "DEBUG_LOW",
            f"SHOW: Initialised VisualiserFactory while displaying columns={columns}",
        )
        return self

    def render(self, urban_layer_geodataframe: gpd.GeoDataFrame) -> Any:
        """Render the visualisation using the provided data.

        Creates and renders a visualiser instance with the configured options.

        Args:
            urban_layer_geodataframe (gpd.GeoDataFrame): The `GeoDataFrame` to visualise.

        Returns:
            Any: The visualisation output (e.g., a map widget or figure).

        Raises:
            ValueError: If _type or _columns are not set, or if invalid style keys are used.

        Examples:
            >>> map_viz = VisualiserFactory().with_type("InteractiveVisualiser")\
            ...     .show("neighborhood")\
            ...     .render(neighborhoods_gdf)
        """
        if self._type is None:
            raise ValueError("Visualiser type must be specified.")
        if self._columns is None:
            raise ValueError("Columns to visualise must be specified.")

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
        """Build and return the configured visualiser instance.

        Creates a visualiser instance for use in pipelines or deferred rendering.

        !!! note "To Keep In Mind"
            Prefer `render()` for immediate visualisation; use `build()` for pipelines.

        Returns:
            VisualiserBase: A configured visualiser instance.

        Raises:
            ValueError: If _type is not set.

        Examples:
            >>> visualiser = mapper.visual.with_type("StaticVisualiser")\
            ...     .with_style({"figsize": (10, 8)})\
            ...     .build()

        """
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
        """Generate a preview of the configured visualiser.

        Shows the visualiser’s configuration in the specified format.

        Args:
            format (str): The format to display ("ascii" or "json"). Defaults to "ascii".

        Raises:
            ValueError: If format is unsupported.

        Examples:
            >>> factory = mappper.visual.with_type("InteractiveVisualiser").build()
            >>> factory.preview(format="json")
        """
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
        """Configure the factory to display a preview after building.

        Enables automatic preview after `build()` or `render()`.

        Args:
            format (str): The preview format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            VisualiserFactory: Self for chaining.

        Examples:
            >>> visualiser = mapper.visual.with_type("InteractiveVisualiser")\
            ...     .with_preview(format="json")\
            ...     .build()
        """
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
