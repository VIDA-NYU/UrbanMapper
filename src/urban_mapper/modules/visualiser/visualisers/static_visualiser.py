import geopandas as gpd
from beartype import beartype
from typing import Any, List
from matplotlib.lines import Line2D

from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase


@beartype
class StaticVisualiser(VisualiserBase):
    """A visualiser that creates static plots using Matplotlib.

    This visualiser generates static visualisations of geographic data using
    Matplotlib. It supports plotting a single column from the GeoDataFrame.

    !!! tip "Available Style Options"
        Common style keys for `StaticVisualiser` include:
        - `figsize`: Figure size as a tuple (width, height).
        - `cmap`: Colormap for numeric data.
        - `color`: Colour for non-numeric data.
        - `markersize`: Size of markers.
        - `legend`: Whether to show a legend.
        - `vmin`: Minimum value for color scaling.
        - `vmax`: Maximum value for color scaling.

    Attributes:
        short_name (str): Short identifier for the visualiser.
        allowed_style_keys (set): Valid style parameters that can be provided.
        style (dict): Style parameters applied to the visualisation.

    Examples:
        >>> from urban_mapper.modules.visualiser import StaticVisualiser
        >>> viz = StaticVisualiser()
        >>> viz.render(
        ...     urban_layer_geodataframe=streets_gdf,
        ...     columns=["street_name"],
        ...     figsize=(10, 8),
        ...     cmap="viridis"
        ... )

    """

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
        """Render a static plot of the GeoDataFrame.

        Creates a static Matplotlib plot for the specified column.
        It renders each source (data_id column) with different markers, when the GeoDataFrame has data_id column

        !!! note "To Keep in Mind"
            Only supports visualisation of a single column at a time.

        Args:
            urban_layer_geodataframe (gpd.GeoDataFrame): The GeoDataFrame to visualise.
            columns (List[str]): A list with a single column name to plot.
            **kwargs: Additional parameters for customising the plot,
                overriding any style parameters set during initialisation.

        Returns:
            Any: A Matplotlib figure object.

        Raises:
            ValueError: If more than one column is specified.
        """
        if len(columns) > 1:
            raise ValueError("StaticVisualiser only supports a single column.")
        render_kwargs = {**self.style, **kwargs}

        if "data_id" in urban_layer_geodataframe:
            data_ids = urban_layer_geodataframe.data_id.dropna().unique()
            data_ids.sort()

            marker_list = list(Line2D.markers)
            marker_list = marker_list[2:]  ## discard point (.) and pixel (,)
            marker_list = marker_list[: len(data_ids)]

            col = urban_layer_geodataframe[~urban_layer_geodataframe.data_id.isna()][
                columns[0]
            ]
            vmin_val = col.min()
            vmax_val = col.max()

            ax = None
            legend = []

            for id, marker in zip(data_ids, marker_list):
                urban_layer_gdf = urban_layer_geodataframe[
                    urban_layer_geodataframe.data_id == id
                ]
                ax = urban_layer_gdf.plot(
                    column=columns[0],
                    legend=id == data_ids[-1],
                    ax=ax,
                    marker=marker,
                    vmin=vmin_val,
                    vmax=vmax_val,
                    **render_kwargs,
                )
                legend.append(
                    Line2D([], [], color="gray", marker=marker, ls="", label=id)
                )

            ax.legend(handles=legend)
        else:
            ax = urban_layer_geodataframe.plot(
                column=columns[0], legend=True, **render_kwargs
            )
        return ax.get_figure()

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this static visualiser.

        Provides a summary of the visualiser's configuration.

        Args:
            format (str): The output format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            Any: A string (for "ascii") or dict (for "json") representing the visualiser.

        Raises:
            ValueError: If format is unsupported.

        Examples:
            >>> viz = StaticVisualiser()
            >>> print(viz.preview())
            Visualiser: StaticVisualiser using Matplotlib
        """
        if format == "ascii":
            return "Visualiser: StaticVisualiser using Matplotlib"
        elif format == "json":
            return {
                "visualiser": "StaticVisualiser using Matplotlib",
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
