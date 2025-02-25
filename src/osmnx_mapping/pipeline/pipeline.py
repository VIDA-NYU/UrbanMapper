from typing import Tuple, Any, List, Union
import geopandas as gpd
import networkx as nx
import joblib
from beartype import beartype
from sklearn.utils._bunch import Bunch

from osmnx_mapping.pipeline import PipelineExecutor
from osmnx_mapping.pipeline import PipelineValidator
from osmnx_mapping.modules.loader import LoaderBase
from osmnx_mapping.modules.preprocessing import GeoImputerBase
from osmnx_mapping.modules.network import NetworkBase
from osmnx_mapping.modules.enricher import EnricherBase
from osmnx_mapping.modules.visualiser import VisualiserBase


@beartype
class UrbanPipeline:
    def __init__(
        self,
        steps: List[
            Tuple[
                str,
                Union[
                    LoaderBase,
                    GeoImputerBase,
                    NetworkBase,
                    EnricherBase,
                    VisualiserBase,
                    Any,  # Support for any future step
                ],
            ]
        ],
    ) -> None:
        self.steps = steps
        self.validator = PipelineValidator(steps)
        self.executor = PipelineExecutor(steps)

    @property
    def named_steps(self) -> Bunch:
        return Bunch(**dict(self.steps))

    @beartype
    def get_step_names(self) -> List[str]:
        return [name for name, _ in self.steps]

    @beartype
    def get_step(self, name: str) -> Any:
        for step_name, step_instance in self.steps:
            if step_name == name:
                return step_instance
        raise KeyError(f"Step '{name}' not found in pipeline.")

    @beartype
    def compose(
        self, latitude_column_name: str, longitude_column_name: str
    ) -> "UrbanPipeline":
        self.executor.compose(latitude_column_name, longitude_column_name)
        return self

    @beartype
    def transform(
        self,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self.executor.transform()

    @beartype
    def compose_transform(
        self, latitude_column_name: str, longitude_column_name: str
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self.executor.compose_transform(
            latitude_column_name, longitude_column_name
        )

    @beartype
    def visualise(self, result_column: str, **kwargs: Any) -> Any:
        return self.executor.visualise(result_column, **kwargs)

    @beartype
    def save(self, filepath: str) -> None:
        joblib.dump(self, filepath)

    @staticmethod
    @beartype
    def load(filepath: str) -> "UrbanPipeline":
        return joblib.load(filepath)

    def __getitem__(self, key: str) -> Any:
        return self.get_step(key)
