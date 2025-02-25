from typing import Tuple, Any, List, Optional, Dict
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.pipeline import UrbanPipeline
import joblib
from sklearn.utils._bunch import Bunch
from osmnx_mapping.utils.helpers import require_attributes


class UrbanPipelineMixin:
    @beartype
    def __init__(self, steps: Optional[List[Tuple[str, Any]]] = None) -> None:
        self._pipeline: Optional[UrbanPipeline] = (
            UrbanPipeline(steps) if steps else None
        )

    @beartype
    def urban_pipeline(self, steps: List[Tuple[str, Any]]) -> UrbanPipeline:
        self._pipeline = UrbanPipeline(steps)
        return self._pipeline

    @property
    @require_attributes(["_pipeline"])
    def named_steps(self) -> Optional[Bunch]:
        return self._pipeline.named_steps

    @beartype
    @require_attributes(["_pipeline"])
    def get_step_names(self) -> List[str]:
        return self._pipeline.get_step_names()

    @beartype
    @require_attributes(["_pipeline"])
    def get_step(self, name: str) -> Any:
        return self._pipeline.get_step(name)

    @beartype
    @require_attributes(["_pipeline"])
    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        return self._pipeline.get_params(deep=deep)

    @beartype
    @require_attributes(["_pipeline"])
    def set_params(self, **kwargs) -> "UrbanPipelineMixin":
        self._pipeline.set_params(**kwargs)
        return self

    @beartype
    @require_attributes(["_pipeline"])
    def compose(self, latitude_column_name: str, longitude_column_name: str) -> None:
        self._pipeline.compose(latitude_column_name, longitude_column_name)

    @beartype
    @require_attributes(["_pipeline"])
    def transform(
        self,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self._pipeline.transform()

    @beartype
    @require_attributes(["_pipeline"])
    def compose_transform(
        self,
        latitude_column_name: str,
        longitude_column_name: str,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self._pipeline.compose_transform(
            latitude_column_name, longitude_column_name
        )

    @beartype
    @require_attributes(["_pipeline"])
    def visualise(self, result_column: str, **kwargs: Any) -> Any:
        return self._pipeline.visualise(result_column, **kwargs)

    @beartype
    @require_attributes(["_pipeline"])
    def save(self, filepath: str) -> None:
        self._pipeline.save(filepath)

    @beartype
    def load(self, filepath: str) -> UrbanPipeline:
        return joblib.load(filepath)

    @require_attributes(["_pipeline"])
    def __getitem__(self, key: str) -> Any:
        return self._pipeline[key]
