import geopandas as gpd
from typing import Any, List
import ipywidgets as widgets
from IPython.display import display
from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase
from beartype import beartype


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
    }

    def _render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        if not columns:
            raise ValueError("At least one column must be specified.")
        render_kwargs = {**self.style, **kwargs}

        def get_map(column):
            return urban_layer_geodataframe.explore(column=column, **render_kwargs)

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
            return {
                "visualiser": "InteractiveVisualiser using Folium",
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
