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

    def _inject_dependencies(self, instance: Any) -> None:
        if (
            hasattr(instance, "nodes")
            and getattr(instance, "nodes", None) is None
            and self.nodes is not None
        ):
            setattr(instance, "nodes", self.nodes)
        if (
            hasattr(instance, "graph")
            and getattr(instance, "graph", None) is None
            and self.graph is not None
        ):
            setattr(instance, "graph", self.graph)
        if (
            hasattr(instance, "edges")
            and getattr(instance, "edges", None) is None
            and self.edges is not None
        ):
            setattr(instance, "edges", self.edges)

    @beartype
    def compose(self, latitude_column_name: str, longitude_column_name: str) -> None:
        if not any(isinstance(step, NetworkBase) for _, step in self.steps):
            raise ValueError("Pipeline must include at least one NetworkBase step.")

        for name, step in self.steps:
            if hasattr(step, "latitude_column_name"):
                setattr(step, "latitude_column_name", latitude_column_name)
            if hasattr(step, "longitude_column_name"):
                setattr(step, "longitude_column_name", longitude_column_name)

        data = None
        network_step = next(
            (name, step) for name, step in self.steps if isinstance(step, NetworkBase)
        )

        network_step_name, network_instance = network_step
        graph, nodes, edges = network_instance.build_network(render=False)
        self.data, self.graph, self.nodes, self.edges = data, graph, nodes, edges

        for current_step_name, current_instance in [
            (step_name, step_instance)
            for step_name, step_instance in self.steps
            if step_name != network_step_name
        ]:
            self.data, self.graph, self.nodes, self.edges = data, graph, nodes, edges
            self._inject_dependencies(current_instance)

            if isinstance(current_instance, LoaderBase):
                data = current_instance.load_data_from_file()
            elif isinstance(current_instance, (GeoImputerBase, GeoFilterBase)):
                if data is None:
                    raise ValueError(
                        f"Step '{current_step_name}' requires data, but no data is available yet."
                    )
                data = current_instance.transform(data)
            elif isinstance(current_instance, EnricherBase):
                if data is None or graph is None or nodes is None or edges is None:
                    raise ValueError(
                        f"Step '{current_step_name}' requires data, graph, nodes, and edges, but some are missing."
                    )

                if network_instance is not None:
                    data = network_instance.map_nearest_nodes(
                        data,
                        output_column="nearest_node",
                        reset_output_column=True,
                        longitude_column=longitude_column_name,
                        latitude_column=latitude_column_name,
                    )

                data, graph, nodes, edges = current_instance.enrich(
                    data, graph, nodes, edges
                )

        self.data, self.graph, self.nodes, self.edges = data, graph, nodes, edges
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
    def visualise(self, result_column: str, **kwargs: Any) -> Any:
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
        return visualiser.render(self.graph, self.edges, result_column, **kwargs)
