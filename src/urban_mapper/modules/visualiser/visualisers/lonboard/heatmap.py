from __future__ import annotations

from typing import Any, ClassVar, Dict, Optional, Set, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from beartype import beartype

from lonboard import HeatmapLayer, Map

from .base import LonboardBaseVisualiser


@beartype
class LonboardHeatmapVisualiser(LonboardBaseVisualiser):
    """Render Lonboard heatmaps from point-based GeoDataFrames

    This visualiser differs from the original, classic Lonboard visualiser by
    focusing on heatmap generation from point data. It utilises `lonboard.HeatmapLayer`
    to create density-based visualisations, making it ideal for urban layers where
    point concentration is of interest.

    !!! tip "Styling via `with_style`"
        Configure the visualiser through the factory, for example:

            mapper.visual.with_type("lonboard_heatmap").with_style({
                "layer_kwargs": {"radius_pixels": 60, "opacity": 0.8},
                "map_kwargs": {
                    "basemap": MaplibreBasemap(
                        mode="interleaved",
                        style=CartoStyle.DarkMatterNoLabels,
                    ),
                    "show_tooltip": True,
                },
            }).build()

        `layer_kwargs` are forwarded to `lonboard.HeatmapLayer` while
        `map_kwargs` tweak the surrounding `lonboard.Map` container.

        See further in: https://developmentseed.org/lonboard/latest/api/layers/heatmap-layer/

    !!! warning "Geometry Requirements"
        Heatmaps require `Point` or `MultiPoint` geometries. Mixed geometry
        types will raise a validation error prior to rendering.
    """

    short_name = "lonboard_heatmap"
    allowed_style_keys = LonboardBaseVisualiser.map_passthrough_keys | {
        "layer_kwargs",
        "map_kwargs",
    }
    colormap_supported_targets: ClassVar[Set[str]] = set()

    def _validate_geometries(self, gdf: gpd.GeoDataFrame) -> None:
        """Ensure the GeoDataFrame only contains point geometries

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to validate.

        Raises:
            ValueError: If non-point geometries are present.
        """
        geom_types = set(gdf.geometry.geom_type.unique())
        valid_types = {"Point", "MultiPoint"}
        if not geom_types.issubset(valid_types):
            raise ValueError(
                "LonboardHeatmapVisualiser requires Point or MultiPoint geometries."
                f" Found geometry types: {geom_types}" if geom_types else ""
            )

    def _create_map(
        self,
        gdf: gpd.GeoDataFrame,
        selected_column: str,
        render_options: Dict[str, Any],
        colormap_values: Optional[Tuple[str, np.ndarray]],
        data_override: Optional[gpd.GeoDataFrame],
    ) -> Map:
        """Build the Lonboard heatmap layer and map

        Args:
            gdf (gpd.GeoDataFrame): Prepared GeoDataFrame containing point geometries.
            selected_column (str): Column providing heatmap weights.
            render_options (Dict[str, Any]): Validated rendering options.
            colormap_values (Optional[Tuple[str, np.ndarray]]): Ignored for heatmaps, present for API parity.
            data_override (Optional[gpd.GeoDataFrame]): Optional GeoDataFrame used in place of `gdf` when provided.

        Returns:
            Map: Lonboard map with a configured `lonboard.HeatmapLayer`.

        Raises:
            ValueError: If `selected_column` cannot be converted to numeric
                weights.
        """
        data_for_layer = data_override if data_override is not None else gdf

        layer_kwargs: Dict[str, Any] = {**(render_options.get("layer_kwargs") or {})}
        weight_array: Optional[np.ndarray]
        if "get_weight" not in layer_kwargs:
            weights = pd.to_numeric(data_for_layer[selected_column], errors="coerce")
            if weights.isna().all():
                raise ValueError(
                    f"Column '{selected_column}' cannot be converted to numeric weights for the heatmap."
                )
            weight_array = weights.fillna(0.0).astype(float).to_numpy()
            layer_kwargs["get_weight"] = weight_array
        else:
            weight_array = None

        if "color_domain" not in layer_kwargs:
            if weight_array is None:
                inferred = pd.to_numeric(
                    data_for_layer[selected_column], errors="coerce"
                ).fillna(0.0)
                weight_array = inferred.astype(float).to_numpy()
            if weight_array.size == 0:
                min_weight = 0.0
                max_weight = 0.0
            else:
                min_weight = float(weight_array.min())
                max_weight = float(weight_array.max())
            if np.isclose(max_weight, min_weight):
                max_weight = min_weight + 1.0
            layer_kwargs["color_domain"] = [min(0.0, min_weight), max_weight]

        layer = HeatmapLayer.from_geopandas(data_for_layer, **layer_kwargs)
        return Map(layer, **(render_options.get("map_kwargs") or {}))
