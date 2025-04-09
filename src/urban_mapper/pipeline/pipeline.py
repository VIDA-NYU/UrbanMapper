import datetime
import json
import os
import uuid
from pathlib import Path
from typing import Tuple, Any, List, Union, Optional

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
    def compose(self) -> "UrbanPipeline":
        self.executor.compose()
        return self

    @require_attributes_not_none("steps")
    def transform(self) -> Tuple[gpd.GeoDataFrame, UrbanLayerBase]:
        return self.executor.transform()

    @require_attributes_not_none("steps")
    def compose_transform(self) -> Tuple[gpd.GeoDataFrame, UrbanLayerBase]:
        return self.executor.compose_transform()

    @require_attributes_not_none("steps")
    def visualise(self, result_columns: Union[str, List[str]], **kwargs: Any) -> Any:
        return self.executor.visualise(result_columns, **kwargs)

    @require_attributes_not_none("steps")
    def save(self, filepath: str) -> None:
        path = Path(filepath)
        if path.suffix != ".dill":
            raise ValueError("Filepath must have '.dill' extension.")
        with open(filepath, "wb") as f:
            dill.dump(self, f)

    @staticmethod
    def load(filepath: str) -> "UrbanPipeline":
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
