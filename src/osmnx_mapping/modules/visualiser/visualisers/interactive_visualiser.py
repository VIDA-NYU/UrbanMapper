import networkx as nx
import geopandas as gpd
from typing import Any, Optional, Dict, Union, List
from beartype import beartype
import ipywidgets as widgets
from IPython.display import display

from osmnx_mapping.modules.visualiser.abc_visualiser import VisualiserBase


class InteractiveVisualiser(VisualiserBase):
    @beartype
    def _render(
        self,
        graph: nx.MultiDiGraph,
        edges: gpd.GeoDataFrame,
        result_columns: Union[str, List[str]],
        colormap: Optional[str] = "Greens",
        legend_keywords: Optional[Dict[str, Any]] = None,
        tile_provider: Optional[str] = "CartoDB positron",
        **kwargs,
    ) -> Any:
        legend_keywords = legend_keywords or {
            "caption": "Aggregated Value",
            "colorbar": True,
        }
        edges_converted = edges.to_crs(self.coordinate_reference_system)

        if isinstance(result_columns, str):
            fmap = edges_converted.explore(
                column=result_columns,
                cmap=colormap,
                legend=True,
                legend_kwds=legend_keywords,
                tiles=tile_provider,
            )
            return fmap

        dropdown_options = result_columns
        dropdown = widgets.Dropdown(
            options=dropdown_options,
            value=result_columns[0],
            description="Viz. with:",
        )
        output = widgets.Output()

        def on_change(change):
            with output:
                output.clear_output()
                selected_column = change["new"]
                fmap = edges_converted.explore(
                    column=selected_column,
                    cmap=colormap,
                    legend=True,
                    legend_kwds=legend_keywords,
                    tiles=tile_provider,
                )
                display(fmap)

        dropdown.observe(on_change, names="value")

        # The following is a bug discovered.
        # PyWidget seems to be buggy at first viz. Double calling makes it appearing automatically.
        for _ in range(2):
            with output:
                output.clear_output()
                fmap = edges_converted.explore(
                    column=result_columns[0],
                    cmap=colormap,
                    legend=True,
                    legend_kwds=legend_keywords,
                    tiles=tile_provider,
                )
                display(fmap)

        return widgets.VBox([dropdown, output])
