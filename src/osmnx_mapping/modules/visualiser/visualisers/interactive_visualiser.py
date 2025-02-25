import folium
import networkx as nx
import geopandas as gpd
from typing import Any, Optional, Dict
from beartype import beartype

from osmnx_mapping.modules.visualiser.abc_visualiser import VisualiserBase


class InteractiveVisualiser(VisualiserBase):
    @beartype
    def _render(
        self,
        graph: nx.MultiDiGraph,
        edges: gpd.GeoDataFrame,
        result_column: str,
        colormap: Optional[str] = "Greens",
        legend_keywords: Optional[Dict[str, Any]] = None,
        tile_provider: Optional[str] = "CartoDB positron",
        **kwargs,
    ) -> folium.Map:
        legend_keywords = legend_keywords or {
            "caption": "Aggregated Value",
            "colorbar": True,
        }
        edges_converted = edges.to_crs(self.coordinate_reference_system)
        fmap = edges_converted.explore(
            column=result_column,
            cmap=colormap,
            legend=True,
            legend_kwds=legend_keywords,
            tiles=tile_provider,
        )
        return fmap
