from beartype import beartype
from .abc_enricher import EnricherBase
from .aggregator import SimpleAggregator, CountAggregator
from .factory.config import EnricherConfig
from .factory.validation import (
    validate_group_by,
    validate_action,
    validate_aggregation_method,
    validate_enricher_type,
)
from .factory.preview import PreviewBuilder
from .factory.registries import ENRICHER_REGISTRY
from osmnx_mapping.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)
import importlib
import inspect
import pkgutil
from pathlib import Path

from osmnx_mapping.config import ENRICHER_NAMESPACE


class EnricherFactory:
    """
    A factory for creating ready-to-use enrichers to enhance street network data.

    Examples:
        # Count taxi trips per street segment
        enricher = (EnricherFactory()
                    .with_data(group_by="nearest_node")
                    .count_by(edge_method="sum", output_column="total_trips")
                    .build())

        # Aggregate number of floors per street segment
        enricher = (EnricherFactory()
                    .with_data(group_by="nearest_node", values_from="numfloors")
                    .aggregate_with("mean", edge_method="average")
                    .build())
    """

    def __init__(self):
        self.config = EnricherConfig()

    @beartype
    def with_data(self, *args, **kwargs) -> "EnricherFactory":
        self.config.with_data(*args, **kwargs)
        return self

    @beartype
    def aggregate_with(self, *args, **kwargs) -> "EnricherFactory":
        self.config.aggregate_with(*args, **kwargs)
        return self

    @beartype
    def count_by(self, *args, **kwargs) -> "EnricherFactory":
        self.config.count_by(*args, **kwargs)
        return self

    @beartype
    def using_enricher(self, *args, **kwargs) -> "EnricherFactory":
        self.config.using_enricher(*args, **kwargs)
        return self

    @beartype
    def preview(self, format: str = "ascii") -> str:
        preview_builder = PreviewBuilder(self.config, ENRICHER_REGISTRY)
        return preview_builder.build_preview(format=format)

    @beartype
    def build(self) -> EnricherBase:
        validate_group_by(self.config)
        validate_action(self.config)
        validate_enricher_type(self.config.enricher_type)

        if self.config.action == "aggregate":
            validate_aggregation_method(self.config.aggregator_config["method"])
            aggregator = SimpleAggregator(
                group_by_column=self.config.group_by[0],
                value_column=self.config.values_from[0],
                aggregation_function=AGGREGATION_FUNCTIONS[
                    self.config.aggregator_config["method"]
                ],
            )
        elif self.config.action == "count":
            aggregator = CountAggregator(
                group_by_column=self.config.group_by[0],
                count_function=len,
            )
        else:
            raise ValueError("Unknown action.")

        enricher_class = ENRICHER_REGISTRY[self.config.enricher_type]
        return enricher_class(
            aggregator=aggregator,
            output_column=self.config.enricher_config["output_column"],
            edge_method=self.config.enricher_config["edge_method"],
            config=self.config,
        )

    @classmethod
    def _initialise(cls):
        package_dir = Path(__file__).parent / "enrichers"
        for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
            try:
                module = importlib.import_module(f"{ENRICHER_NAMESPACE}.{module_name}")
                for class_name, class_object in inspect.getmembers(
                    module, inspect.isclass
                ):
                    if (
                        issubclass(class_object, EnricherBase)
                        and class_object is not EnricherBase
                        and class_name not in ENRICHER_REGISTRY
                    ):
                        from .factory.registries import register_enricher

                        register_enricher(class_name, class_object)
            except ImportError as error:
                print(f"Warning: Failed to load enricher module {module_name}: {error}")


EnricherFactory._initialise()
