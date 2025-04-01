from typing import List, Tuple, Union, Dict, Any, Type
from beartype import beartype

from urban_mapper.modules.imputer import GeoImputerBase
from urban_mapper.modules.filter import GeoFilterBase
from urban_mapper.modules.loader import LoaderBase
from urban_mapper.modules.enricher import EnricherBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.visualiser import VisualiserBase
from urban_mapper.config.container import container


@beartype
class PipelineValidator:
    def __init__(
        self,
        steps: List[
            Tuple[
                str,
                Union[
                    UrbanLayerBase,
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

            cls = instance.__class__
            found = False
            for base_class in self.pipeline_schema.keys():
                if issubclass(cls, base_class):
                    step_counts[base_class] += 1
                    found = True
                    break
            if not found:
                raise TypeError(
                    f"Step '{name}' is not an instance of a valid step class."
                    f"It is currently of type '{cls.__name__}'. "
                    f"Did you forget to call .build() on this step?"
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
