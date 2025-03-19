import json
from typing import Tuple, Any, List, Union
import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.loader import LoaderBase
from urban_mapper.modules.imputer import GeoImputerBase
from urban_mapper.modules.filter import GeoFilterBase
from urban_mapper.modules.enricher import EnricherBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.visualiser import VisualiserBase
from urban_mapper.pipeline.executor import PipelineExecutor
from urban_mapper.pipeline.validator import PipelineValidator
import joblib
from sklearn.utils._bunch import Bunch

from urban_mapper.utils import require_attributes_not_none


@beartype
class UrbanPipeline:
    def __init__(
        self,
        steps: Union[
            None,
            List[
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
        ] = None,
    ) -> None:
        self.steps = steps
        if steps:
            self.validator = PipelineValidator(steps)
            self.executor = PipelineExecutor(steps)

    @require_attributes_not_none("steps")
    @property
    def named_steps(self) -> Bunch:
        return Bunch(**dict(self.steps))

    @require_attributes_not_none("steps")
    def get_step_names(self) -> List[str]:
        return [name for name, _ in self.steps]

    @require_attributes_not_none("steps")
    def get_step(self, name: str) -> Any:
        for step_name, step_instance in self.steps:
            if step_name == name:
                return step_instance
        raise KeyError(f"Step '{name}' not found in pipeline.")

    @require_attributes_not_none("steps")
    def compose(
        self,
    ) -> "UrbanPipeline":
        self.executor.compose()
        return self

    @require_attributes_not_none("steps")
    def transform(self) -> Tuple[gpd.GeoDataFrame, UrbanLayerBase]:
        return self.executor.transform()

    @require_attributes_not_none("steps")
    def compose_transform(
        self,
    ) -> Tuple[gpd.GeoDataFrame, UrbanLayerBase]:
        return self.executor.compose_transform()

    @require_attributes_not_none("steps")
    def visualise(self, result_columns: Union[str, List[str]], **kwargs: Any) -> Any:
        return self.executor.visualise(result_columns, **kwargs)

    @require_attributes_not_none("steps")
    def save(self, filepath: str) -> None:
        joblib.dump(self, filepath)

    @staticmethod
    def load(filepath: str) -> "UrbanPipeline":
        return joblib.load(filepath)

    def __getitem__(self, key: str) -> Any:
        return self.get_step(key)

    @require_attributes_not_none("steps")
    def _preview(self, format: str = "ascii") -> Union[dict, str]:
        if format == "json":
            preview_data = {
                "pipeline": {
                    "steps": [
                        {
                            "name": name,
                            "preview": step.preview(format="json")
                            if hasattr(step, "preview")
                            else "No preview available",
                        }
                        for name, step in self.steps
                    ]
                }
            }
            return preview_data
        else:
            preview_lines = ["Urban Pipeline Preview:"]
            for i, (name, step) in enumerate(self.steps, 1):
                if hasattr(step, "preview"):
                    step_preview = step.preview(format="ascii").replace("\n", "\n    ")
                    preview_lines.append(f"Step {i}: {name}\n    {step_preview}")
                else:
                    preview_lines.append(f"Step {i}: {name}\n    No preview available")
            return "\n".join(preview_lines)

    @require_attributes_not_none("steps")
    def preview(self, format: str = "ascii") -> None:
        if not self.steps:
            print("No Steps available to preview.")
            return
        preview_data = self._preview(format=format)
        if format == "ascii":
            print(preview_data)
        elif format == "json":
            print(json.dumps(preview_data, indent=2, default=str))
        else:
            raise ValueError(f"Unsupported format '{format}'.")
