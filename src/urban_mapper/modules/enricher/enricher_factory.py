from typing import Optional, Union
from beartype import beartype
from .abc_enricher import EnricherBase
from .aggregator import SimpleAggregator, CountAggregator
from .factory.config import EnricherConfig
from .factory.validation import (
    validate_group_by,
    validate_action,
    validate_aggregation_method,
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
    def __init__(self):
        self.config = EnricherConfig()
        self._instance: Optional[EnricherBase] = None
        self._preview: Optional[dict] = None

    def with_data(self, *args, **kwargs) -> "EnricherFactory":
        self.config.with_data(*args, **kwargs)
        return self

    def aggregate_by(self, *args, **kwargs) -> "EnricherFactory":
        self.config.aggregate_by(*args, **kwargs)
        return self

    def count_by(self, *args, **kwargs) -> "EnricherFactory":
        self.config.count_by(*args, **kwargs)
        return self

    def with_type(self, primitive_type: str) -> "EnricherFactory":
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
        self._preview = {"format": format}
        return self

    def build(self) -> EnricherBase:
        validate_group_by(self.config)
        validate_action(self.config)

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
            raise ValueError(
                "Unknown action. Please open an issue on GitHub to request such feature."
            )

        enricher_class = ENRICHER_REGISTRY[self.config.enricher_type]
        self._instance = enricher_class(
            aggregator=aggregator,
            output_column=self.config.enricher_config["output_column"],
            config=self.config,
        )
        if self._preview is not None:
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
