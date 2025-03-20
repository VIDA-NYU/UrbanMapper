from typing import Tuple, Optional, Any, List, Union
import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.loader import LoaderBase
from urban_mapper.modules.imputer import GeoImputerBase
from urban_mapper.modules.filter import GeoFilterBase
from urban_mapper.modules.enricher import EnricherBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.visualiser import VisualiserBase


@beartype
class PipelineExecutor:
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
        self.data: Optional[gpd.GeoDataFrame] = None
        self.urban_layer: Optional[UrbanLayerBase] = None
        self._composed: bool = False

    def compose(
        self,
    ) -> None:
        if self._composed:
            raise ValueError(
                "Pipeline already composed. Please re instantiate your pipeline and its steps."
            )
        urban_layer_step = next(
            (
                (name, step)
                for name, step in self.steps
                if isinstance(step, UrbanLayerBase)
            ),
            None,
        )
        if urban_layer_step is None:
            raise ValueError("Pipeline must include exactly one UrbanLayerBase step.")
        urban_layer_name, urban_layer_instance = urban_layer_step

        loader_step = next(
            ((name, step) for name, step in self.steps if isinstance(step, LoaderBase)),
            None,
        )
        if loader_step is None:
            raise ValueError("Pipeline must include exactly one LoaderBase step.")
        loader_name, loader_instance = loader_step
        self.data = loader_instance.load_data_from_file()

        for name, step in self.steps:
            if isinstance(step, GeoImputerBase):
                self.data = step.transform(self.data, urban_layer_instance)

        for name, step in self.steps:
            if isinstance(step, GeoFilterBase):
                self.data = step.transform(self.data, urban_layer_instance)

        _, mapped_data = urban_layer_instance.map_nearest_layer(
            self.data,
        )
        self.data = mapped_data

        for name, step in self.steps:
            if isinstance(step, EnricherBase):
                urban_layer_instance = step.enrich(self.data, urban_layer_instance)

        self.urban_layer = urban_layer_instance
        self._composed = True

    def transform(self) -> Tuple[gpd.GeoDataFrame, UrbanLayerBase]:
        if not self._composed:
            raise ValueError("Pipeline not composed. Call compose() first.")
        return self.data, self.urban_layer

    def compose_transform(
        self,
    ) -> Tuple[gpd.GeoDataFrame, UrbanLayerBase]:
        self.compose()
        return self.transform()

    def visualise(self, result_columns: Union[str, List[str]], **kwargs: Any) -> Any:
        if not self._composed:
            raise ValueError("Pipeline not composed. Call compose() first.")
        visualiser = next(
            (
                instance
                for _, instance in self.steps
                if isinstance(instance, VisualiserBase)
            ),
            None,
        )
        if not visualiser:
            raise ValueError("No VisualiserBase step defined.")
        return visualiser.render(
            urban_layer_geodataframe=self.urban_layer.layer,
            columns=result_columns,
            **kwargs,
        )
