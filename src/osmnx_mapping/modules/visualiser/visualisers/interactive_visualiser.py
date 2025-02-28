import networkx as nx
import geopandas as gpd
from typing import Any, Optional, Dict, Union, List
from beartype import beartype
import ipywidgets as widgets
from IPython.display import display
from folium import Map

from osmnx_mapping.modules.visualiser.abc_visualiser import VisualiserBase


class InteractiveVisualiser(VisualiserBase):
    @beartype
    def _render(
        self,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        result_columns: Union[str, List[str]],
        target: str = "edges",
        colormap: Optional[str] = "Greens",
        legend_keywords: Optional[Dict[str, Any]] = None,
        tile_provider: Optional[str] = "CartoDB positron",
        **kwargs,
    ) -> Any:
        if target not in ["nodes", "edges", "both"]:
            raise ValueError("target must be 'nodes', 'edges', or 'both'")

        legend_keywords = legend_keywords or {
            "caption": "Aggregated Value",
            "colorbar": True,
        }
        if not isinstance(legend_keywords, dict):
            raise TypeError("legend_keywords must be a dictionary")

        edges_converted = edges.to_crs(self.coordinate_reference_system)
        nodes_converted = nodes.to_crs(self.coordinate_reference_system)

        if isinstance(result_columns, str):
            result_columns = [result_columns]

        def get_current_column():
            return result_columns[0]

        selected_column = get_current_column()
        if target == "edges" and selected_column not in edges_converted.columns:
            raise ValueError(f"Column '{selected_column}' not found in edges")
        elif target == "nodes" and selected_column not in nodes_converted.columns:
            raise ValueError(f"Column '{selected_column}' not found in nodes")
        elif target == "both":
            if (
                selected_column not in edges_converted.columns
                or selected_column not in nodes_converted.columns
            ):
                raise ValueError(
                    f"Column '{selected_column}' not found in both edges and nodes"
                )

        if target == "edges":
            fmap = edges_converted.explore(
                column=selected_column,
                cmap=colormap,
                legend=True,
                legend_kwds=legend_keywords,
                tiles=tile_provider,
            )
        elif target == "nodes":
            fmap = nodes_converted.explore(
                column=selected_column,
                cmap=colormap,
                legend=True,
                legend_kwds=legend_keywords,
                tiles=tile_provider,
            )
        elif target == "both":
            bounds = edges_converted.total_bounds
            center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
            zoom_start = 12
            fmap = Map(location=center, zoom_start=zoom_start, tiles=tile_provider)

            edges_converted.explore(
                m=fmap,
                column=selected_column,
                cmap=colormap,
                legend=True,
                legend_kwds=legend_keywords,
            )
            nodes_converted.explore(
                m=fmap,
                column=selected_column,
                cmap=colormap,
                legend=True,
                legend_kwds=legend_keywords,
            )

        if len(result_columns) > 1:
            dropdown = widgets.Dropdown(
                options=result_columns,
                value=result_columns[0],
                description="Viz. with:",
            )
            output = widgets.Output()

            def on_change(change):
                with output:
                    output.clear_output()
                    selected_column = change["new"]

                    if (
                        target == "edges"
                        and selected_column not in edges_converted.columns
                    ):
                        raise ValueError(
                            f"Column '{selected_column}' not found in edges"
                        )
                    elif (
                        target == "nodes"
                        and selected_column not in nodes_converted.columns
                    ):
                        raise ValueError(
                            f"Column '{selected_column}' not found in nodes"
                        )
                    elif target == "both":
                        if (
                            selected_column not in edges_converted.columns
                            or selected_column not in nodes_converted.columns
                        ):
                            raise ValueError(
                                f"Column '{selected_column}' not found in both edges and nodes"
                            )

                    if target == "edges":
                        fmap = edges_converted.explore(
                            column=selected_column,
                            cmap=colormap,
                            legend=True,
                            legend_kwds=legend_keywords,
                            tiles=tile_provider,
                        )
                    elif target == "nodes":
                        fmap = nodes_converted.explore(
                            column=selected_column,
                            cmap=colormap,
                            legend=True,
                            legend_kwds=legend_keywords,
                            tiles=tile_provider,
                        )
                    elif target == "both":
                        bounds = edges_converted.total_bounds
                        center = [
                            (bounds[1] + bounds[3]) / 2,
                            (bounds[0] + bounds[2]) / 2,
                        ]
                        zoom_start = 12
                        fmap = Map(
                            location=center, zoom_start=zoom_start, tiles=tile_provider
                        )
                        edges_converted.explore(
                            m=fmap,
                            column=selected_column,
                            cmap=colormap,
                            legend=True,
                            legend_kwds=legend_keywords,
                        )
                        nodes_converted.explore(
                            m=fmap,
                            column=selected_column,
                            cmap=colormap,
                            legend=True,
                            legend_kwds=legend_keywords,
                        )
                    display(fmap)

            dropdown.observe(on_change, names="value")

            with output:
                display(fmap)

            return widgets.VBox([dropdown, output])

        return fmap
