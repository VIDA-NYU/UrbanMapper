from typing import Tuple, Optional, Any, List, Union
import geopandas as gpd
import networkx as nx
from beartype import beartype
from osmnx_mapping.modules.loader import LoaderBase
from osmnx_mapping.modules.preprocessing import GeoImputerBase, GeoFilterBase
from osmnx_mapping.modules.network import NetworkBase
from osmnx_mapping.modules.enricher import EnricherBase
from osmnx_mapping.modules.visualiser import VisualiserBase


@beartype
class PipelineExecutor:
    def __init__(
        self,
        steps: List[
            Tuple[
                str,
                Union[
                    NetworkBase,
                    LoaderBase,
                    GeoImputerBase,
                    GeoFilterBase,
                    EnricherBase,
                    VisualiserBase,
                    Any,
                ],
            ]
        ],
    ) -> None:
        self.steps = steps
        self.data: Optional[gpd.GeoDataFrame] = None
        self.graph: Optional[nx.MultiDiGraph] = None
        self.nodes: Optional[gpd.GeoDataFrame] = None
        self.edges: Optional[gpd.GeoDataFrame] = None
        self._composed: bool = False

    def _inject_network_dependencies(self, instance: Any) -> None:
        if hasattr(instance, "nodes") and getattr(instance, "nodes", None) is None:
            setattr(instance, "nodes", self.nodes)
        if hasattr(instance, "graph") and getattr(instance, "graph", None) is None:
            setattr(instance, "graph", self.graph)
        if hasattr(instance, "edges") and getattr(instance, "edges", None) is None:
            setattr(instance, "edges", self.edges)

    def _inject_latitude_longitude_columns(
        self, instance: Any, latitude_column_name: str, longitude_column_name: str
    ) -> None:
        if (
            hasattr(instance, "latitude_column_name")
            and getattr(instance, "latitude_column_name", None) is None
        ):
            setattr(instance, "latitude_column_name", latitude_column_name)
        if (
            hasattr(instance, "longitude_column_name")
            and getattr(instance, "longitude_column_name", None) is None
        ):
            setattr(instance, "longitude_column_name", longitude_column_name)

    @beartype
    def compose(self, latitude_column_name: str, longitude_column_name: str) -> None:
        network_step = next(
            (name, step) for name, step in self.steps if isinstance(step, NetworkBase)
        )
        if not network_step:
            raise ValueError("Pipeline must include a NetworkBase step.")
        network_name, network_instance = network_step

        self.graph, self.nodes, self.edges = network_instance.build_network(
            render=False
        )

        for name, step in self.steps:
            self._inject_latitude_longitude_columns(
                instance=step,
                latitude_column_name=latitude_column_name,
                longitude_column_name=longitude_column_name,
            )

        for current_step_name, current_instance in [
            (step_name, step_instance)
            for step_name, step_instance in self.steps
            if step_name != network_name
        ]:
            self._inject_network_dependencies(current_instance)

            if isinstance(current_instance, LoaderBase):
                self.data = current_instance.load_data_from_file()
            elif isinstance(current_instance, (GeoImputerBase, GeoFilterBase)):
                if self.data is None:
                    raise ValueError(f"Step '{current_step_name}' requires data.")
                self.data = current_instance.transform(self.data)

        if self.data is not None and network_instance.mappings:
            for mapping in network_instance.mappings:
                mapping_type = mapping["type"]
                lon_column = mapping["lon"]
                lat_column = mapping["lat"]
                output_column = mapping["output"]
                if mapping_type == "node":
                    self.data = network_instance.map_nearest_nodes(
                        self.data, lon_column, lat_column, output_column
                    )
                elif mapping_type == "edge":
                    self.data = network_instance.map_nearest_edges(
                        self.data, lon_column, lat_column, output_column
                    )

        for name, step in self.steps:
            if isinstance(step, EnricherBase):
                if self.data is None or self.graph is None:
                    raise ValueError(f"Step '{name}' requires data and graph.")
                self.data, self.graph, self.nodes, self.edges = step.enrich(
                    self.data, self.graph, self.nodes, self.edges
                )

        self._composed = True

    @beartype
    def transform(
        self,
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        if not self._composed:
            raise ValueError("Pipeline not composed. Call compose() first.")
        return self.data, self.graph, self.nodes, self.edges

    @beartype
    def compose_transform(
        self, latitude_column_name: str, longitude_column_name: str
    ) -> Tuple[gpd.GeoDataFrame, nx.MultiDiGraph, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        self.compose(latitude_column_name, longitude_column_name)
        return self.transform()

    @beartype
    def visualise(self, result_columns: Union[str, List[str]], **kwargs: Any) -> Any:
        if not self._composed:
            raise ValueError("Pipeline not composed. Call compose() first.")
        visualiser = next(
            (
                instance
                for _, instance in self.steps
                if isinstance(instance, VisualiserBase)
            ),
            None,
        )
        if not visualiser:
            raise ValueError("No VisualiserBase step defined.")
        return visualiser.render(
            graph=self.graph,
            nodes=self.nodes,
            edges=self.edges,
            result_columns=result_columns,
            **kwargs,
        )
