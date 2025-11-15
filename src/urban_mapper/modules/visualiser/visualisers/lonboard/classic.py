from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import geopandas as gpd
import numpy as np
from beartype import beartype

from lonboard import Map, viz

from .base import LonboardBaseVisualiser


@beartype
class LonboardClassicVisualiser(LonboardBaseVisualiser):
    """Render Lonboard Viz handler with polygon fills

    This visualiser wraps `lonboard.viz` so polygons, lines, and points
    may share a single map. See further in: https://developmentseed.org/lonboard/latest/api/viz/

    !!! tip "Styling via `with_style`"
        Configure the visualiser through the factory, for example:

            mapper.visual.with_type("lonboard_classic").with_style({
                "polygon_kwargs": {"get_fill_color": "#3268a8"},
                "map_kwargs": {
                    "basemap": MaplibreBasemap(
                        mode="interleaved",
                        style=CartoStyle.DarkMatterNoLabels,
                    ),
                    "show_tooltip": True,
                },
            }).build()

        Accepted keys include `polygon_kwargs` (forwarded to
        `lonboard.PolygonLayer`), `map_kwargs` for `lonboard.Map`, and a
        `colormap` resolved to `get_fill_color` (generic to all polygon layers).

        See further in: https://developmentseed.org/lonboard/latest/api/layers/polygon-layer/
    """

    short_name = "lonboard_classic"
    allowed_style_keys = LonboardBaseVisualiser.map_passthrough_keys | {
        "polygon_kwargs",
        "scatterplot_kwargs",
        "map_kwargs",
        "colormap",
        "polygon_colormap",
    }
    allow_polygon_colormap_alias = True

    colormap_supported_targets = {"polygon", "scatterplot", "point"}
    default_colormap_target = "scatterplot"

    def _create_map(
        self,
        gdf: gpd.GeoDataFrame,
        selected_column: str,
        render_options: Dict[str, Any],
        colormap_values: Optional[Tuple[str, np.ndarray]],
        data_override: Optional[gpd.GeoDataFrame],
    ) -> Map:
        """Build the composite Lonboard map for classic visualisations

        Args:
            gdf (gpd.GeoDataFrame): Prepared GeoDataFrame containing geometry and data columns.
            selected_column (str): Column currently visualised.
            render_options (Dict[str, Any]): Validated rendering options.
            colormap_values (Optional[Tuple[str, np.ndarray]]): Optional layer target and colour array resolved
                by the base class.
            data_override (Optional[gpd.GeoDataFrame]): Alternate GeoDataFrame to visualise instead of `gdf`.

        Returns:
            Map: Lonboard map highlighting filled polygons with optional line and
            point overlays.
        """
        polygon_kwargs: Dict[str, Any] = {
            **(render_options.get("polygon_kwargs") or {})
        }
        scatterplot_kwargs: Dict[str, Any] = {
            **(render_options.get("scatterplot_kwargs") or {})
        }

        if colormap_values is not None:
            target, colour_array = colormap_values
            if target == "polygon":
                polygon_kwargs.setdefault("get_fill_color", colour_array)
            elif target in ("scatterplot", "point"):
                scatterplot_kwargs.setdefault("get_fill_color", colour_array)

        map_kwargs: Dict[str, Any] = render_options.get("map_kwargs", {})
        data_for_viz = data_override if data_override is not None else gdf

        return viz(
            data_for_viz,
            scatterplot_kwargs=scatterplot_kwargs,
            polygon_kwargs=polygon_kwargs,
            map_kwargs=map_kwargs,
        )