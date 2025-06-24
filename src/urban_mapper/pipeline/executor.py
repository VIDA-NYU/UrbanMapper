from typing import Tuple, Optional, Any, List, Union, Dict
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
    """Executor for `Pipeline Steps` in `UrbanMapper Pipeline`.

    Orchestrates the execution of pipeline `steps` in a `predefined order`, managing `data loading`,
    `processing`, and `enrichment`. As a bonus, it also displays a progress bar during execution.

    Attributes:
        steps (List[Tuple[str, Union[UrbanLayerBase, LoaderBase, GeoImputerBase, GeoFilterBase, EnricherBase, VisualiserBase, Any]]]):
            List of (name, component) tuples representing the pipeline steps.
        data (Optional[gpd.GeoDataFrame]): Processed GeoDataFrame, populated after execution.
        urban_layer (Optional[UrbanLayerBase]): Enriched urban layer instance, set after execution.
        _composed (bool): Indicates if the pipeline has been composed.

    Examples:
        >>> import urban_mapper as um
        >>> from urban_mapper.pipeline import UrbanPipeline
        >>> mapper = um.UrbanMapper()
        >>> steps = [
        ...     ("loader", mapper.loader.from_file("data.csv").with_columns("lon", "lat").build()),
        ...     ("streets", mapper.urban_layer.with_type("streets_roads").from_place("London, UK").build())
        ... ]
        >>> executor = UrbanPipeline(steps)
        >>> executor.compose()
        >>> data, layer = executor.transform()
        >>> 👆 Hint: You can `compose_transform()` all in one go!
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
        self.data: Optional[Dict[str, gpd.GeoDataFrame]] = None
        self.urban_layer: Optional[UrbanLayerBase] = None
        self._composed: bool = False

    def compose(
        self,
    ) -> None:
        """Compose and Execute Pipeline Steps.

        !!! tip "Steps Execution Order"
            - [x] Load datasets
            - [x] Apply imputers
            - [x] Apply filters
            - [x] Map to urban layer
            - [x] Enrich urban layer

        Raises:
            ValueError: If pipeline is already composed or lacks required steps (loader, urban layer).

        Examples:
            >>> executor.compose()  # Executes all steps with progress updates
        """
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

        num_loaders = sum(isinstance(step, LoaderBase) for _, step in self.steps)
        num_imputers = sum(isinstance(step, GeoImputerBase) for _, step in self.steps)
        num_filters = sum(isinstance(step, GeoFilterBase) for _, step in self.steps)
        num_enrichers = sum(isinstance(step, EnricherBase) for _, step in self.steps)
        total_steps = 1 + num_loaders + num_imputers + num_filters + num_enrichers

        if num_loaders == 0:
            raise ValueError("Pipeline must include exactly one LoaderBase step.")

        with alive_bar(
            total_steps,
            title="Pipeline Progress",
            force_tty=True,
            dual_line=False,
        ) as bar:
            self.data = None if num_loaders == 1 else {}

            for name, step in self.steps:
                if isinstance(step, LoaderBase):
                    bar()
                    bar.title = f"~> Loading: {name}..."

                    if num_loaders == 1:
                        self.data = step.load_data_from_file()
                    else:
                        self.data[name] = step.load_data_from_file()

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

    def transform(
        self,
    ) -> Tuple[
        Union[
            Dict[str, gpd.GeoDataFrame],
            gpd.GeoDataFrame,
        ],
        UrbanLayerBase,
    ]:
        """Retrieve Results of `Pipeline Execution`.

        Returns processed data and enriched urban layer post-composition.

        Returns:
            Tuple[Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame], UrbanLayerBase]: Processed data and urban layer.

        Raises:
            ValueError: If pipeline hasn’t been composed.

        Examples:
            >>> data, layer = executor.transform()
        """
        if not self._composed:
            raise ValueError("Pipeline not composed. Call compose() first.")
        return self.data, self.urban_layer

    def compose_transform(
        self,
    ) -> Tuple[
        Union[
            Dict[str, gpd.GeoDataFrame],
            gpd.GeoDataFrame,
        ],
        UrbanLayerBase,
    ]:
        """Compose and Transform in One Step.

        Combines compose and transform operations.

        Returns:
            Tuple[Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame], UrbanLayerBase]: Processed data and urban layer.

        Raises:
            ValueError: If pipeline is already composed or lacks required steps.

        Examples:
            >>> data, layer = executor.compose_transform()
        """
        self.compose()
        return self.transform()

    def visualise(self, result_columns: Union[str, List[str]], **kwargs: Any) -> Any:
        """Visualise Pipeline Results.

        Uses the pipeline’s visualiser to display results based on specified columns.

        !!! note "If no visualiser is defined"
            If no visualiser is defined in the pipeline, a ValueError will be raised.

            Please make sure to include a visualiser step in your pipeline.

        Args:
            result_columns: Column(s) to visualise from the urban layer.
            **kwargs: Additional arguments for the visualiser’s render method.

        Returns:
            Any: Visualisation output, type depends on visualiser.

        Raises:
            ValueError: If pipeline isn’t composed or lacks a visualiser.

        Examples:
            >>> executor.visualise(result_columns="count")
        """
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
