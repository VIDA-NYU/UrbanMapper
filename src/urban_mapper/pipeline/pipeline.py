import datetime
import json
import os
import uuid
from pathlib import Path
from typing import Tuple, Any, List, Union, Optional, Dict

import dill
import geopandas as gpd
import pandas as pd
from beartype import beartype
from jupytergis import GISDocument
from sklearn.utils._bunch import Bunch
from urban_mapper import logger
from urban_mapper.modules.enricher import EnricherBase
from urban_mapper.modules.filter import GeoFilterBase
from urban_mapper.modules.imputer import GeoImputerBase
from urban_mapper.modules.loader import LoaderBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.visualiser import VisualiserBase
from urban_mapper.pipeline.executor import PipelineExecutor
from urban_mapper.pipeline.validator import PipelineValidator
from urban_mapper.utils import require_attributes_not_none


@beartype
class UrbanPipeline:
    """`Scikit-Learn` Inspired `Pipeline` for `Urban Mapper`.

    Constructs and manages pipelines integrating various urban mapper components into a cohesive workflow,
    handling execution order and data flow. Yet, not only, you also can `save`, `share`, `export`, and `load pipelines`,
    is not that great for reproducibility?

    Have a look at how a pipeline could look like:

    <div class="mermaid">
    %%{init: {
    'theme': 'base',
    'themeVariables': {
    'primaryColor': '#57068c',
    'primaryTextColor': '#fff',
    'primaryBorderColor': '#F49BAB',
    'lineColor': '#F49BAB',
    'secondaryColor': '#9B7EBD',
    'tertiaryColor': '#E5D9F2'
      }
    }}%%
    graph LR
        subgraph "Data Ingestion"
            A["Loaders (1..*)"]
            B["Urban Layer (1)"]
            A -->|Raw data| B
        end
        subgraph "Data Preprocessing"
            direction TB
            C["Imputers (0..*)"]
            D["Filters (0..*)"]
            C -->|Imputed data| D
        end
        subgraph "Data Processing"
            E["Enrichers (1..*)"]
        end
        subgraph "Data Output"
            F["Visualiser (0, 1)"]
        end

        B -->|Spatial data| C
        D -->|Filtered data| E
        E -->|Enriched data| F
    </div>

    <p style="text-align: center; font-style: italic;">
      Notation: (1) = exactly one instance, (0..*) = zero or more instances, (1..*) = one or more instances, (0, 1) = zero or one instance
    </p>


    !!! note
        `Pipelines` must be `composed` before `transforming` or `visualising` data.
        Use `compose()` or `compose_transform()`.

    Attributes:
        steps (List[Tuple[str, Union[UrbanLayerBase, LoaderBase, GeoImputerBase, GeoFilterBase, EnricherBase, VisualiserBase, Any]]]):
            List of (name, component) tuples defining pipeline steps.
        validator (PipelineValidator): Validates step compatibility.
        executor (PipelineExecutor): Executes the pipeline steps.

    Examples:
        >>> import urban_mapper as um
        >>> from urban_mapper.pipeline import UrbanPipeline
        >>> mapper = um.UrbanMapper()
        >>> steps = [
        ...     ("loader", mapper.loader.from_file("taxi_data.csv").with_columns("lng", "lat").build()),
        ...     ("streets", mapper.urban_layer.with_type("streets_roads").from_place("London, UK").build()),
        ...     ("count_pickups", mapper.enricher.with_data(group_by="nearest_streets").count_by(output_column="pickup_count").build()),
        ...     ("visualiser", mapper.visualiser.with_type("InteractiveVisualiser").build())
        ... ]
        >>> pipeline = UrbanPipeline(steps)
        >>> data, layer = pipeline.compose_transform()
        >>> pipeline.visualise(["pickup_count"])

    """

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
        """Access steps by name using attribute syntax.

        !!! note "Mimicking the following by Sckit-learn"
            This property allows accessing pipeline steps using attribute-style access.
            For example, `pipeline.named_steps.loader` returns the loader step.

            See more in [named_steps of Sklearn](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.named_steps)

        Returns:
            Bunch: Object with step names as attributes.

        Raises:
            ValueError: If no steps are defined.

        Examples:
            >>> pipeline.named_steps.loader
        """
        return Bunch(**dict(self.steps))

    @require_attributes_not_none("steps")
    def get_step_names(self) -> List[str]:
        """List all step names in the pipeline.

        Returns:
            List[str]: Names of all steps.

        Raises:
            ValueError: If no steps are defined.

        Examples:
            >>> names = pipeline.get_step_names()
        """
        return [name for name, _ in self.steps]

    @require_attributes_not_none("steps")
    def get_step(self, name: str) -> Any:
        """Retrieve a step by its name.

        Args:
            name: Name of the step to retrieve.

        Returns:
            Any: The step’s component instance.

        Raises:
            KeyError: If step name doesn’t exist.
            ValueError: If no steps are defined.

        Examples:
            >>> loader = pipeline.get_step("loader")
        """
        for step_name, step_instance in self.steps:
            if step_name == name:
                return step_instance
        raise KeyError(f"Step '{name}' not found in pipeline.")

    @require_attributes_not_none("steps")
    def compose(self) -> "UrbanPipeline":
        """Prepare pipeline for execution without transforming.

        Validates and sets up the pipeline for subsequent transformation.

        Returns:
            UrbanPipeline: Self for chaining.

        Raises:
            ValueError: If no steps or steps are invalid.

        Examples:
            >>> pipeline.compose()
        """
        self.executor.compose()
        return self

    @require_attributes_not_none("steps")
    def transform(
        self,
    ) -> Tuple[
        Union[
            Dict[str, gpd.GeoDataFrame],
            gpd.GeoDataFrame,
        ],
        UrbanLayerBase,
    ]:
        """Execute pipeline transformation.

        Returns processed data and enriched urban layer after composition.

        Returns:
            Tuple[Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame], UrbanLayerBase]: Processed data and urban layer.

        Raises:
            ValueError: If no steps or not composed.

        Examples:
            >>> data, layer = pipeline.transform()
        """
        return self.executor.transform()

    @require_attributes_not_none("steps")
    def compose_transform(
        self,
    ) -> Tuple[
        Union[
            Dict[str, gpd.GeoDataFrame],
            gpd.GeoDataFrame,
        ],
        UrbanLayerBase,
    ]:
        """Compose and transform in one step.

        Combines composition and transformation into a single operation.

        Returns:
            Tuple[Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame], UrbanLayerBase]: Processed data and urban layer.

        Raises:
            ValueError: If no steps or steps are invalid.

        Examples:
            >>> data, layer = pipeline.compose_transform()
        """
        return self.executor.compose_transform()

    @require_attributes_not_none("steps")
    def visualise(self, result_columns: Union[str, List[str]], **kwargs: Any) -> Any:
        """Visualise pipeline results.

        Displays results using the pipeline’s visualiser.

        Args:
            result_columns: Column(s) to visualise. If more than one a widget is being displayed to select which one to visualise.
            **kwargs: Additional arguments for the visualiser.

        Returns:
            Any: Visualisation output, type depends on visualiser.

        Raises:
            ValueError: If no steps, not composed, or no visualiser.

        Examples:
            >>> pipeline.visualise(result_columns="count")
        """
        return self.executor.visualise(result_columns, **kwargs)

    @require_attributes_not_none("steps")
    def save(self, filepath: str) -> None:
        """Save pipeline to a file.

        Serialises the pipeline and its state using dill.

        Explore more about [Dill, here](https://github.com/uqfoundation/dill).

        !!! note "What if I have custom lambda functions in my own script/cell? How is that saved?"
            If you have custom lambda functions, no worries Dill deals with them pretty neatly.
            Obviously it could increase the size of the object.

        Args:
            filepath: Path to save file, must end with '.dill'.

        Raises:
            ValueError: If filepath lacks '.dill' or no steps.
            IOError: If file cannot be written.

        Examples:
            >>> pipeline.save("my_pipeline.dill")
        """
        path = Path(filepath)
        if path.suffix != ".dill":
            raise ValueError("Filepath must have '.dill' extension.")
        with open(filepath, "wb") as f:
            dill.dump(self, f)

    @staticmethod
    def load(filepath: str) -> "UrbanPipeline":
        """Load pipeline from a file.

        Deserialises a previously saved pipeline. From another paper, a friend, a teammate.

        Args:
            filepath: Path to the saved pipeline file.

        Returns:
            UrbanPipeline: Loaded pipeline instance.

        Raises:
            FileNotFoundError: If file doesn’t exist.
            IOError: If file cannot be read.

        Examples:
            >>> pipeline = um.UrbanPipeline.load("my_pipeline.dill")
        """
        with open(filepath, "rb") as f:
            pipeline = dill.load(f)
        if not pipeline.executor._composed:
            print(
                "WARNING: ",
                "Loaded pipeline has not been composed. Make sure to call compose() "
                "before using methods that require composition.",
            )
        return pipeline

    def __getitem__(self, key: str) -> Any:
        """Access step by name using dictionary syntax.

        Args:
            key: Name of the step.

        Returns:
            Any: Step’s component instance.

        Raises:
            KeyError: If step name doesn’t exist.

        Examples:
            >>> loader = pipeline["loader"]
        """
        return self.get_step(key)

    @require_attributes_not_none("steps")
    def _preview(self, format: str = "ascii") -> Union[dict, str]:
        """Generate a pipeline preview.

        Creates a representation of the pipeline and its steps. Calling in cascade,
        all steps' `.preview()` methods.

        Args:
            format: Output format ("ascii" or "json").

        Returns:
            Union[dict, str]: Preview as dictionary or string.
        """
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
        """Display pipeline preview.

        Prints a summary of the pipeline and its steps.Calling in cascade,
        all steps' `.preview()` methods.

        Args:
            format: Output format ("ascii" or "json").

        Raises:
            ValueError: If format is unsupported or no steps.

        Examples:
            >>> pipeline.preview()
        """
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

    @require_attributes_not_none("steps")
    def to_jgis(
        self,
        filepath: str,
        base_maps=None,
        include_urban_layer: bool = True,
        urban_layer_name: str = "Enriched Layer",
        urban_layer_type: Optional[str] = None,
        urban_layer_opacity: float = 1.0,
        additional_layers=None,
        zoom: int = 20,
        raise_on_existing: bool = True,
        **kwargs,
    ) -> None:
        """Export pipeline results to JupyterGIS document.

        !!! question "What is JupyterGIS?"

            JupyterGIS is a library that provides interactive & collaborative mapping capabilities in real time,
            all throughout your Jupyter notebooks' workflow.

            See [their documentation for further details](https://jupytergis.readthedocs.io/en/latest/).

            Creates an interactive map visualisation saved as a `.jgis` file.

        Args:
            filepath: Path to save the .jgis file.
            base_maps: List of base map configurations (default: None).
            include_urban_layer: Include urban layer in output (default: True).
            urban_layer_name: Name for urban layer (default: "Enriched Layer").
            urban_layer_type: Visualisation type (default: None, auto-detected).
            urban_layer_opacity: Layer opacity (default: 1.0).
            additional_layers: Extra layers to include (default: None).
            zoom: Initial map zoom level (default: 20).
            raise_on_existing: Raise error if file exists (default: True).
            **kwargs: Additional visualisation arguments.

        Raises:
            ValueError: If no steps or not composed.
            ImportError: If JupyterGIS isn’t installed.
            FileExistsError: If file exists and raise_on_existing is True.

        Examples:
            >>> pipeline.to_jgis("map.jgis")
        """
        if additional_layers is None:
            additional_layers = []
        if base_maps is None:
            base_maps = [
                {
                    "url": "http://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
                    "attribution": "© OpenStreetMap contributors",
                    "name": "Base Map",
                    "opacity": 0.9,
                }
            ]
        if GISDocument is None:
            raise ImportError(
                "jupytergis is required for this functionality. "
                "Install it with `uv add jupytergis`."
            )
        if not self.executor._composed:
            raise ValueError("Pipeline not composed. Call compose() first.")

        if filepath and os.path.exists(filepath):
            if raise_on_existing:
                raise FileExistsError(
                    f"File already exists: {filepath}. "
                    f"Set raise_on_existing=False for less strictness or delete the file prior to running `to_jgis()`."
                )
            else:
                path = Path(filepath)
                stem = path.stem
                suffix = path.suffix
                random_str = uuid.uuid4().hex[:8]
                new_stem = f"{stem}_{random_str}"
                new_filepath = path.with_name(f"{new_stem}{suffix}")
                original_filepath = filepath
                filepath = str(new_filepath)
                logger.log(
                    "DEBUG_LOW",
                    f"File exists: {original_filepath}. Using new filename: {filepath}",
                )

        enriched_layer = self.executor.urban_layer.layer
        projection = self.executor.urban_layer.coordinate_reference_system
        bbox = enriched_layer.total_bounds
        extent = [bbox[0], bbox[1], bbox[2], bbox[3]]

        doc = GISDocument(
            path=None,
            projection=projection,
            extent=extent,
            zoom=zoom,
        )

        for bm in base_maps:
            doc.add_raster_layer(
                url=bm["url"],
                name=bm["name"],
                attribution=bm.get("attribution", ""),
                opacity=bm.get("opacity", 1.0),
            )

        if include_urban_layer:
            if urban_layer_type is None:
                geometry_type = enriched_layer.geometry.geom_type.iloc[0]
                if geometry_type in ["Point", "MultiPoint"]:
                    urban_layer_type = "circle"
                elif geometry_type in ["LineString", "MultiLineString"]:
                    urban_layer_type = "line"
                elif geometry_type in ["Polygon", "MultiPolygon"]:
                    urban_layer_type = "fill"
                else:
                    raise ValueError(f"Unsupported geometry type: {geometry_type}")

            enriched_layer = enriched_layer.replace({pd.NaT: None})
            for col in enriched_layer.columns:
                if enriched_layer[col].dtype == "object":
                    enriched_layer[col] = enriched_layer[col].apply(
                        self.serialize_value
                    )

            geojson_data = json.loads(enriched_layer.to_json())
            doc.add_geojson_layer(
                data=geojson_data,
                name=urban_layer_name,
                type=urban_layer_type,
                opacity=urban_layer_opacity,
                **kwargs,
            )

        for layer in additional_layers:
            data = layer["data"]
            if isinstance(data, gpd.GeoDataFrame):
                data = json.loads(data.to_json())
            elif not isinstance(data, dict):
                raise ValueError(
                    "Additional layer 'data' must be a GeoDataFrame or GeoJSON dict."
                )
            layer_type = layer.get("type")
            if layer_type is None:
                features = data["features"]
                if not features:
                    raise ValueError("Empty GeoJSON data in additional layer.")
                geometry_type = features[0]["geometry"]["type"]
                if geometry_type in ["Point", "MultiPoint"]:
                    layer_type = "circle"
                elif geometry_type in ["LineString", "MultiLineString"]:
                    layer_type = "line"
                elif geometry_type in ["Polygon", "MultiPolygon"]:
                    layer_type = "fill"
                else:
                    raise ValueError(f"Unsupported geometry type: {geometry_type}")
            doc.add_geojson_layer(
                data=data,
                name=layer["name"],
                type=layer_type,
                opacity=layer.get("opacity", 1.0),
                **layer.get("kwargs", {}),
            )

        doc.save_as(filepath)

    @staticmethod
    def serialize_value(value):
        if isinstance(value, datetime.datetime) or isinstance(value, pd.Timestamp):
            return value.isoformat()
        return value
