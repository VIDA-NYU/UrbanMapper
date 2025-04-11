from typing import Tuple, Optional, Any, List, Union
import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.loader import LoaderBase
from urban_mapper.modules.imputer import GeoImputerBase
from urban_mapper.modules.filter import GeoFilterBase
from urban_mapper.modules.enricher import EnricherBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.visualiser import VisualiserBase
from alive_progress import alive_bar


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

        num_imputers = sum(isinstance(step, GeoImputerBase) for _, step in self.steps)
        num_filters = sum(isinstance(step, GeoFilterBase) for _, step in self.steps)
        num_enrichers = sum(isinstance(step, EnricherBase) for _, step in self.steps)
        total_steps = 2 + num_imputers + num_filters + num_enrichers

        with alive_bar(
            total_steps,
            title="Pipeline Progress",
            force_tty=True,
            dual_line=False,
        ) as bar:
            bar()
            bar.title = f"~> Loading {loader_name}..."
            self.data = loader_instance.load_data_from_file()

            for name, step in self.steps:
                if isinstance(step, GeoImputerBase):
                    bar()
                    bar.title = f"~> Applying imputer: {name}..."
                    self.data = step.transform(self.data, urban_layer_instance)

            for name, step in self.steps:
                if isinstance(step, GeoFilterBase):
                    bar()
                    bar.title = f"~> Applying filter: {name}..."
                    self.data = step.transform(self.data, urban_layer_instance)

            bar()
            bar.title = (
                f"~> Let's spatial join the {urban_layer_name} layer with the data..."
            )
            _, mapped_data = urban_layer_instance.map_nearest_layer(self.data)
            self.data = mapped_data

            for name, step in self.steps:
                if isinstance(step, EnricherBase):
                    bar()
                    bar.title = f"~> Applying enricher: {name}..."
                    urban_layer_instance = step.enrich(self.data, urban_layer_instance)

            self.urban_layer = urban_layer_instance
            self._composed = True
            bar()
            bar.title = f"🗺️ Successfully composed pipeline with {total_steps} steps!"

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
