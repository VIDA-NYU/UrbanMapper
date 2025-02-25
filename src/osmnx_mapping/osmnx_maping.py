from typing import Optional, Union
import networkx as nx
import geopandas as gpd
import pandas as pd
from beartype import beartype
from osmnx_mapping.config import DEFAULT_CRS
from osmnx_mapping.config.container import container
from osmnx_mapping.utils import LazyMixin


class OSMNxMapping:
    @beartype
    def __init__(self, coordinate_reference_system: str = DEFAULT_CRS):
        self.coordinate_reference_system = coordinate_reference_system

        self.graph: Optional[nx.MultiDiGraph] = None
        self.nodes: Optional[gpd.GeoDataFrame] = None
        self.edges: Optional[gpd.GeoDataFrame] = None
        self.data: Optional[Union[pd.DataFrame, gpd.GeoDataFrame]] = None

        self._instances = {}
        self._mixin_classes = container.mixin_classes()

    def __getattr__(self, name):
        if name in self._mixin_classes:
            if name in self._instances:
                return self._instances[name]
            proxy = LazyMixin(self, name, self._mixin_classes[name])
            self._instances[name] = proxy
            return proxy
        raise AttributeError(
            f"OSMNxMapping has no mixin '{name}', maybe update the config yaml file?"
        )
