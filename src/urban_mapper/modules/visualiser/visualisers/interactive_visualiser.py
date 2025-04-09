import geopandas as gpd
from typing import Any, List
import ipywidgets as widgets
from IPython.display import display
from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase
from beartype import beartype
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import branca.colormap as cm


@beartype
class InteractiveVisualiser(VisualiserBase):
    short_name = "Interactive"
    allowed_style_keys = {
        "cmap",
        "color",
        "m",
        "tiles",
        "attr",
        "tooltip",
        "popup",
        "highlight",
        "categorical",
        "legend",
        "scheme",
        "k",
        "vmin",
        "vmax",
        "width",
        "height",
        "colorbar_text_color",
    }

    def _render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        if not columns:
            raise ValueError("At least one column must be specified.")
        render_kwargs = {**self.style, **kwargs}

        legend = render_kwargs.pop("legend", True)
        text_color = render_kwargs.pop("colorbar_text_color", "black")

        def get_map(column):
            if pd.api.types.is_numeric_dtype(urban_layer_geodataframe[column]):
                vmin = render_kwargs.get("vmin", urban_layer_geodataframe[column].min())
                vmax = render_kwargs.get("vmax", urban_layer_geodataframe[column].max())
                cmap = render_kwargs.get("cmap", "viridis")

                folium_map = urban_layer_geodataframe.explore(
                    column=column, legend=False, **render_kwargs
                )

                if legend:
                    mpl_cmap = plt.get_cmap(cmap)

                    colors = mpl_cmap(np.linspace(0, 1, 256))
                    colors = [tuple(color) for color in colors]
                    colormap = cm.LinearColormap(
                        colors=colors,
                        vmin=vmin,
                        vmax=vmax,
                        caption=column,
                        text_color=text_color,
                    )

                    folium_map.add_child(colormap)
            else:
                folium_map = urban_layer_geodataframe.explore(
                    column=column, legend=legend, **render_kwargs
                )

            return folium_map

        if len(columns) == 1:
            return get_map(columns[0])
        else:
            dropdown = widgets.Dropdown(
                options=columns, value=columns[0], description="Column:"
            )
            output = widgets.Output()

            def on_change(change):
                with output:
                    output.clear_output()
                    display(get_map(change["new"]))

            dropdown.observe(on_change, names="value")
            with output:
                display(get_map(columns[0]))
            return widgets.VBox([dropdown, output])

    def preview(self, format: str = "ascii") -> Any:
        if format == "ascii":
            return "Visualiser: InteractiveVisualiser using Folium"
        elif format == "json":
            return {"visualiser": "InteractiveVisualiser using Folium"}
        else:
            raise ValueError(f"Unsupported format '{format}'")
