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
    """Validator for Pipeline Steps.

    !!! note "The Stricter The Better!"
        To avoid side-effects, the validator is strict about the types of components
        it accepts. The number of components of each type is also strictly enforced.


        | Schema Key  | Component Type    | Class Path                                    | Min | Max       |
        |-------------|-------------------|-----------------------------------------------|-----|-----------|
        | urban_layer | Urban Layer       | `urban_mapper.modules.urban_layer.UrbanLayerBase` | 1   | 1         |
        | loader      | Loader            | `urban_mapper.modules.loader.LoaderBase`         | 1   | 1         |
        | geo_imputer | Geo Imputer       | `urban_mapper.modules.imputer.GeoImputerBase`    | 0   | unlimited |
        | geo_filter  | Geo Filter        | `urban_mapper.modules.filter.GeoFilterBase`      | 0   | unlimited |
        | enricher    | Enricher          | `urban_mapper.modules.enricher.EnricherBase`     | 1   | unlimited |
        | visualiser  | Visualiser        | `urban_mapper.modules.visualiser.VisualiserBase` | 0   | 1         |

        Information About The Table Above

        - [x] **Min** and **Max** indicate the allowed number of components of each type in the pipeline.
        - [x] A **Min** of `1` means the component is required; `0` means it’s optional.
        - [x] **unlimited** in the Max column means you can include as many instances as needed—great for stacking multiple enrichers or filters to enhance your analysis.

    Ensures pipeline steps comply with schema requirements, checking uniqueness, counts, and types.

    Attributes:
        steps (List[Tuple[str, Union[UrbanLayerBase, LoaderBase, GeoImputerBase, GeoFilterBase, EnricherBase, VisualiserBase, Any]]]):
            List of (name, component) tuples to validate.
        pipeline_schema (Dict[Type[Any], Dict[str, int]]): Schema defining step requirements.

    Examples:
        >>> validator = um.PipelineValidator(steps)  # Validation occurs on init
    """

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
        """Validate pipeline steps against schema.

        Checks `uniqueness of names`, `valid types`, and `count constraints`.

        Raises:
            ValueError: If names are duplicated or counts don’t meet schema.
            TypeError: If step type isn’t valid.
        """
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
