import geopandas as gpd
from beartype import beartype
from typing import Any, List

from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase


@beartype
class StaticVisualiser(VisualiserBase):
    short_name = "Static"
    allowed_style_keys = {
        "kind",
        "cmap",
        "color",
        "ax",
        "cax",
        "categorical",
        "legend",
        "scheme",
        "k",
        "vmin",
        "vmax",
        "markersize",
        "figsize",
    }

    def _render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        if len(columns) > 1:
            raise ValueError("StaticVisualiser only supports a single column.")
        render_kwargs = {**self.style, **kwargs}
        ax = urban_layer_geodataframe.plot(
            column=columns[0], legend=True, **render_kwargs
        )
        return ax.get_figure()

    def preview(self, format: str = "ascii") -> Any:
        if format == "ascii":
            return "Visualiser: StaticVisualiser using Matplotlib"
        elif format == "json":
            return {
                "visualiser": "StaticVisualiser using Matplotlib",
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
