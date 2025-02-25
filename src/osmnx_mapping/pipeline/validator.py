from typing import List, Tuple, Union, Dict, Any, Type
from beartype import beartype
from osmnx_mapping.modules.loader import LoaderBase
from osmnx_mapping.modules.preprocessing import (
    GeoImputerBase,
    GeoFilterBase,
)
from osmnx_mapping.modules.network import NetworkBase
from osmnx_mapping.modules.enricher import EnricherBase
from osmnx_mapping.modules.visualiser import VisualiserBase
from osmnx_mapping.config.container import container


@beartype
class PipelineValidator:
    def __init__(
        self,
        steps: List[
            Tuple[
                str,
                Union[
                    NetworkBase,
                    LoaderBase,
                    GeoImputerBase,
                    GeoFilterBase,
                    EnricherBase,
                    VisualiserBase,
                    Any,
                ],
            ]
        ],
    ) -> None:
        self.steps = steps
        self.pipeline_schema = container.pipeline_schema()
        self._validate_steps()

    def _validate_steps(self) -> None:
        step_counts: Dict[Type[Any], int] = {
            cls: 0 for cls in self.pipeline_schema.keys()
        }
        unique_names = set()

        for name, instance in self.steps:
            if name in unique_names:
                raise ValueError(
                    f"Duplicate step name '{name}'. Step names must be unique."
                )
            unique_names.add(name)

            cls = instance.__class__.__mro__[0]
            found = False
            for base_class in self.pipeline_schema.keys():
                if issubclass(cls, base_class):
                    step_counts[base_class] += 1
                    found = True
                    break
            if not found:
                raise ValueError(
                    f"Step '{name}' has invalid type {cls.__name__}. Must be one of: "
                    f"{', '.join(cls.__name__ for cls in self.pipeline_schema.keys())}."
                )

        for base_class, constraints in self.pipeline_schema.items():
            count = step_counts[base_class]
            min_count = constraints["min"]
            max_count = constraints["max"]

            if count < min_count:
                raise ValueError(
                    f"At least {min_count} {base_class.__name__} step(s) required, got {count}."
                )
            if max_count is not None and count > max_count:
                raise ValueError(
                    f"Only {max_count} {base_class.__name__} step(s) allowed, got {count}."
                )
