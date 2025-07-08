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
    """A visualiser that creates interactive web maps with Folium.

    This visualiser generates interactive maps using Folium, allowing for `zooming`,
    `panning`, `layer selection`, `tooltips`, and `popups`. For `multiple columns`, it provides
    a `dropdown` to switch between different data visualisations.

    !!! tip "Available Style Options"
        Common style keys for `InteractiveVisualiser` include:
        - `width`: Width of the map in pixels.
        - `height`: Height of the map in pixels.
        - `color`: Colour for non-numeric data.
        - `opacity`: Transparency level.
        - `tiles`: Base map tiles (e.g., "OpenStreetMap", "CartoDB positron"). See further in [Folium Tiles](https://leaflet-extras.github.io/leaflet-providers/preview/)
        - `tooltip`: Whether to show tooltips on hover.
        - `popup`: Whether to show popups on click.
        - `cmap`: Colormap for numeric data.
        - `legend`: Whether to show a legend.
        - `vmin`: Minimum value for color scaling.
        - `vmax`: Maximum value for color scaling.
        - `colorbar_text_color`: Text color for the color bar.

    Attributes:
        short_name (str): Short identifier for the visualiser.
        allowed_style_keys (set): Valid style parameters that can be provided.
        style (dict): Style parameters applied to the visualisation.

    Examples:
        >>> from urban_mapper.modules.visualiser import InteractiveVisualiser
        >>> viz = InteractiveVisualiser()
        >>> viz.render(
        ...     urban_layer_geodataframe=streets_gdf,
        ...     columns=["street_name"]
        ... )
        >>> viz = InteractiveVisualiser(style={
        ...     "color": "red",
        ...     "opacity": 0.7,
        ...     "tooltip": True,
        ...     "tiles": "CartoDB positron"
        ... })
        >>> viz.render(
        ...     urban_layer_geodataframe=enriched_gdf,
        ...     columns=["nearest_street", "distance_to_street"],
        ...     legend=True
        ... )

    """

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
        "marker_type",
        "marker_kwds",
    }

    def _render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        """Render an interactive map of the GeoDataFrame.

        Creates an interactive Folium map displaying the data. For numeric columns,
        it creates choropleth maps with color scales. For categorical columns, it
        creates categorical maps with distinct colors. When multiple columns are
        provided, it includes a dropdown to switch between them.

        !!! note "To Keep in Mind"
            Requires an internet connection for map tiles and interactivity.

        Args:
            urban_layer_geodataframe (gpd.GeoDataFrame): The GeoDataFrame to visualise.
            columns (List[str]): List of column names to include in the visualisation.
            **kwargs: Additional parameters for customising the visualisation,
                overriding any style parameters set during initialisation.

        Returns:
            Any: A Folium map object for a single column, or an ipywidgets.VBox for multiple columns.

        Raises:
            ValueError: If no columns are specified.
        """
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
        """Generate a preview of this interactive visualiser.

        Provides a summary of the visualiser's configuration.

        Args:
            format (str): The output format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            Any: A string (for "ascii") or dict (for "json") representing the visualiser.

        Raises:
            ValueError: If format is unsupported.

        Examples:
            >>> viz = InteractiveVisualiser()
            >>> print(viz.preview())
            Visualiser: InteractiveVisualiser using Folium
            Style: Default styling
        """
        if format == "ascii":
            style_preview = (
                ", ".join(f"{k}: {v}" for k, v in self.style.items())
                if self.style
                else "Default styling"
            )
            return f"Visualiser: InteractiveVisualiser using Folium\nStyle: {style_preview}"
        elif format == "json":
            return {
                "visualiser": "InteractiveVisualiser",
                "library": "Folium",
                "allowed_style_keys": list(self.allowed_style_keys),
                "current_style": self.style,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
