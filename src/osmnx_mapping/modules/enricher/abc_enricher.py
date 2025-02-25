from abc import ABC, abstractmethod
from typing import Tuple, Callable, Dict, Optional, Any
import geopandas as gpd
import networkx as nx
import pandas as pd
import numpy as np
from beartype import beartype

from osmnx_mapping.utils import require_arguments_not_none


class EnricherBase(ABC):
    EDGE_METHODS: Dict[str, Callable[[pd.Series, pd.Series], float]] = {}

    def __init__(self, config: Optional[Any] = None) -> None:
        from osmnx_mapping.modules.enricher.factory.config import (
            EnricherConfig,
        )

        self.config = config or EnricherConfig()

    @staticmethod
    @beartype
    def reproject_edges(
        edges_dataframe: gpd.GeoDataFrame, target_crs: str
    ) -> gpd.GeoDataFrame:
        if edges_dataframe.crs is None or edges_dataframe.crs.to_string() != target_crs:
            edges_dataframe = edges_dataframe.to_crs(target_crs)
        return edges_dataframe

    @staticmethod
    @beartype
    def ensure_multiindex(edges_dataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        if not isinstance(edges_dataframe.index, pd.MultiIndex):
            if "u" in edges_dataframe.columns and "v" in edges_dataframe.columns:
                if "key" in edges_dataframe.columns:
                    edges_dataframe = edges_dataframe.set_index(
                        ["u", "v", "key"], drop=True
                    )
                else:
                    edges_dataframe = edges_dataframe.set_index(["u", "v"], drop=True)
            else:
                raise ValueError("Edges DataFrame must contain 'u' and 'v' columns.")
        return edges_dataframe

    @staticmethod
    @beartype
    def compute_edge_average(
        edge_row: pd.Series, aggregated_values: pd.Series
    ) -> float:
        node_u, node_v = edge_row["u"], edge_row["v"]
        values = [
            aggregated_values.get(node_u, np.nan),
            aggregated_values.get(node_v, np.nan),
        ]
        values = [v for v in values if not pd.isna(v)]
        return float(np.mean(values)) if values else np.nan

    @staticmethod
    @beartype
    def compute_edge_sum(edge_row: pd.Series, aggregated_values: pd.Series) -> float:
        node_u, node_v = edge_row["u"], edge_row["v"]
        values = [
            aggregated_values.get(node_u, np.nan),
            aggregated_values.get(node_v, np.nan),
        ]
        values = [v for v in values if not pd.isna(v)]
        return float(np.sum(values)) if values else np.nan

    @staticmethod
    @beartype
    def compute_edge_max(edge_row: pd.Series, aggregated_values: pd.Series) -> float:
        node_u, node_v = edge_row["u"], edge_row["v"]
        values = [
            aggregated_values.get(node_u, np.nan),
            aggregated_values.get(node_v, np.nan),
        ]
        values = [v for v in values if not pd.isna(v)]
        return float(np.max(values)) if values else np.nan

    @staticmethod
    @beartype
    def compute_edge_min(edge_row: pd.Series, aggregated_values: pd.Series) -> float:
        node_u, node_v = edge_row["u"], edge_row["v"]
        values = [
            aggregated_values.get(node_u, np.nan),
            aggregated_values.get(node_v, np.nan),
        ]
        values = [v for v in values if not pd.isna(v)]
        return float(np.min(values)) if values else np.nan

    @classmethod
    def _initialise_methods(cls):
        cls.EDGE_METHODS = {
            "average": cls.compute_edge_average,
            "sum": cls.compute_edge_sum,
            "max": cls.compute_edge_max,
            "min": cls.compute_edge_min,
        }

    @abstractmethod
    @beartype
    def _enrich(
        self,
        data: gpd.GeoDataFrame,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        NotImplementedError("_enrich method not implemented.")

    @abstractmethod
    @beartype
    def preview(self, format: str = "ascii") -> str:
        NotImplementedError("Preview method not implemented.")

    @beartype
    @require_arguments_not_none(
        "graph", error_msg="Graph must not be None. Please supply a valid graph."
    )
    def enrich(
        self,
        data: gpd.GeoDataFrame,
        graph: nx.MultiDiGraph,
        nodes: gpd.GeoDataFrame,
        edges: gpd.GeoDataFrame,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        return self._enrich(data, graph, nodes, edges, **kwargs)


EnricherBase._initialise_methods()
