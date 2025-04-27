from typing import Optional, Union
from beartype import beartype
from .abc_enricher import EnricherBase
from .aggregator import SimpleAggregator, CountAggregator
from .factory.config import EnricherConfig
from .factory.validation import (
    validate_group_by,
    validate_action,
)
from .factory.registries import ENRICHER_REGISTRY, register_enricher
from urban_mapper.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)
import importlib
import inspect
import pkgutil
from pathlib import Path
from thefuzz import process


@beartype
class EnricherFactory:
    """Factory Class For Creating and Configuring Data `Enrichers`.

    This class offers a fluent, chaining-methods interface for crafting and setting up
    data `enrichers` in the `UrbanMapper` workflow. `Enrichers` empower spatial aggregation
    and analysis on geographic data—like counting points in polygons or tallying stats
    for regions.

    The factory handles the nitty-gritty of `enricher` instantiation, `configuration`,
    and `application`, ensuring a uniform workflow no matter the enricher type.

    Attributes:
        config: Configuration settings steering the enricher.
        _instance: The underlying enricher instance (internal use only).
        _preview: Preview configuration (internal use only).

    Examples:
        >>> import urban_mapper as um
        >>> import geopandas as gpd
        >>> mapper = um.UrbanMapper()
        >>> hoods = mapper.urban_layer.region_neighborhoods().from_place("London, UK")
        >>> points = gpd.read_file("points.geojson")
        >>> # Count points per neighbourhood
        >>> enriched_hoods = mapper.enricher\
        ...     .with_type("SingleAggregatorEnricher")\ # By default not needed as this is the default / only one at the moment.
        ...     .with_data(group_by="neighbourhood")\
        ...     .count_by(output_column="point_count")\
        ...     .build()\
        ...     .enrich(points, hoods)
    """

    def __init__(self):
        self.config = EnricherConfig()
        self._instance: Optional[EnricherBase] = None
        self._preview: Optional[dict] = None

    def with_data(self, *args, **kwargs) -> "EnricherFactory":
        """Specify columns to group by and values to aggregate.

        Sets up which columns to group data by and, optionally, which to pull
        values from for aggregation during enrichment.

        Args:
            group_by: Column name(s) to group by. Can be a string or list of strings.
            values_from: Column name(s) to aggregate. Optional; if wanted, must be a string.

        Returns:
            The EnricherFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher.with_data(group_by="neighbourhood")
        """
        self.config.with_data(*args, **kwargs)
        return self

    def with_debug(self, debug: bool = True) -> "EnricherFactory":
        """Toggle debug mode for the enricher.

        Enables or disables debug mode, which can spill extra info during enrichment.

        !!! note "What Extra Info?"
            For instance, we will be able to have an extra column for each enrichments that shows which indices
            were taken from the original data to apply the enrichment. This is useful to understand
            how the enrichment was done and to debug any issues that may arise. Another one may also be
            for some Machine learning-based tasks that would require so.

        Args:
            debug: Whether to turn on debug mode (default: True). # Such a parameter might be needed when stacking `.with_debug()`, and trying to `false` the behaviour rather than deleting the line.
        Returns:
            The EnricherFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher.with_debug(True)
        """
        self.config.debug = debug
        return self

    def aggregate_by(self, *args, **kwargs) -> "EnricherFactory":
        """Set the enricher to perform aggregation operations.

        Configures the enricher to aggregate data (e.g., `sum`, `mean`) using provided args.

        !!! tip "Available Methods"

            - [x] `sum`
            - [x] `mean`
            - [x] `median`
            - [x] `min`
            - [x] `max`

        Args:
            *args: Positional args for EnricherConfig.aggregate_by.
            **kwargs: Keyword args like `group_by`, `values_from`, `method` (e.g., "sum").

        Returns:
            The EnricherFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher\
            ...     .with_data(group_by="neighbourhood", values_from="temp")\
            ...     .aggregate_by(method="mean", output_column="avg_temp")
        """
        self.config.aggregate_by(*args, **kwargs)
        return self

    def count_by(self, *args, **kwargs) -> "EnricherFactory":
        """Set the enricher to count features.

        Configures the enricher to count items per group—great for tallying points in areas.

        Args:
            *args: Positional args for EnricherConfig.count_by.
            **kwargs: Keyword args like `group_by`, `output_column`.

        Returns:
            The EnricherFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher\
            ...     .with_data(group_by="pickup")\
            ...     .count_by(output_column="pickup_count")
        """
        self.config.count_by(*args, **kwargs)
        return self

    def with_type(self, primitive_type: str) -> "EnricherFactory":
        """Choose the enricher type to create.

        Sets the type of enricher, dictating the enrichment approach, from the registry.

        !!! note "At the moment only one exists"

            - [x] `SingleAggregatorEnricher` (default)

            Hence, no need use `with_type` unless you want to use a different one in the future.
            Furthermore, we kept it for compatibility with other modules.

        Args:
            primitive_type: Name of the enricher type (e.g., "SingleAggregatorEnricher").

        Returns:
            The EnricherFactory instance for chaining.

        Raises:
            ValueError: If the type isn’t in the registry.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher.with_type("SingleAggregatorEnricher")
        """
        if primitive_type not in ENRICHER_REGISTRY:
            available = list(ENRICHER_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            if score > 80:
                suggestion = f" Maybe you meant '{match}'?"
            else:
                suggestion = ""
            raise ValueError(
                f"Unknown enricher type '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self.config.with_type(primitive_type)
        return self

    def preview(self, format: str = "ascii") -> Union[None, str, dict]:
        """Show a preview of the configured enricher.

        Displays a sneak peek of the enricher setup in the chosen format.

        Args:
            format: Preview format—"ascii" (text) or "json" (dict).

        Returns:
            None for "ascii" (prints to console), dict for "json".

        Raises:
            ValueError: If format isn’t supported.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher\
            ...     .with_data(group_by="pickup")\
            ...     .count_by()\
            ...     .build()
            >>> enricher.preview()
        """
        if self._instance is None:
            print("No Enricher instance available to preview.")
            return None
        if hasattr(self._instance, "preview"):
            preview_data = self._instance.preview(format=format)
            if format == "ascii":
                print(preview_data)
            elif format == "json":
                return preview_data
            else:
                raise ValueError(f"Unsupported format '{format}'.")
        else:
            print("Preview not supported for this Enricher instance.")
        return None

    def with_preview(self, format: str = "ascii") -> "EnricherFactory":
        """Set the factory to show a preview after building.

        Configures an automatic preview post-build—handy for a quick check.

        Args:
            format: Preview format—"ascii" (default, text) or "json" (dict).

        Returns:
            The EnricherFactory instance for chaining.

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher\
            ...     .with_data(group_by="pickup")\
            ...     .count_by()\
            ...     .with_preview()
        """
        self._preview = {"format": format}
        return self

    def build(self) -> EnricherBase:
        """Build and return the configured enricher instance.

        Finalises the setup, validates it, and creates the enricher with its aggregator.

        Returns:
            An EnricherBase-derived instance tailored to the factory’s settings.

        Raises:
            ValueError: If config is invalid (e.g., missing params).

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher\
            ...     .with_type("SingleAggregatorEnricher")\
            ...     .with_data(group_by="pickup")\
            ...     .count_by(output_column="pickup_count")\
            ...     .build()
        """
        validate_group_by(self.config)
        validate_action(self.config)

        if self.config.action == "aggregate":
            method = self.config.aggregator_config["method"]
            if isinstance(method, str):
                if method not in AGGREGATION_FUNCTIONS:
                    raise ValueError(f"Unknown aggregation method '{method}'")
                aggregation_function = AGGREGATION_FUNCTIONS[method]
            elif callable(method):
                aggregation_function = method
            else:
                raise ValueError("Aggregation method must be a string or a callable")
            aggregator = SimpleAggregator(
                group_by_column=self.config.group_by[0],
                value_column=self.config.values_from[0],
                aggregation_function=aggregation_function,
            )
        elif self.config.action == "count":
            aggregator = CountAggregator(
                group_by_column=self.config.group_by[0],
                count_function=len,
            )
        else:
            raise ValueError(
                "Unknown action. Please open an issue on GitHub to request such feature."
            )

        enricher_class = ENRICHER_REGISTRY[self.config.enricher_type]
        self._instance = enricher_class(
            aggregator=aggregator,
            output_column=self.config.enricher_config["output_column"],
            config=self.config,
        )
        if self._preview:
            self.preview(format=self._preview["format"])
        return self._instance


def _initialise():
    package_dir = Path(__file__).parent / "enrichers"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(
                f".enrichers.{module_name}", package=__package__
            )
            for class_name, class_object in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(class_object, EnricherBase)
                    and class_object is not EnricherBase
                ):
                    register_enricher(class_name, class_object)
        except ImportError as error:
            print(f"Warning: Failed to load enrichers module {module_name}: {error}")


_initialise()
