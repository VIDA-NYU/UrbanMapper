from beartype import beartype
from osmnx_mapping.modules.network.abc_network import NetworkBase
from osmnx_mapping.modules.network.networks.osmnx_network import OSMNxNetwork
from osmnx_mapping.utils.helpers import (
    require_arguments_not_none,
    require_attributes_not_none,
)


class NetworkFactory:
    def __init__(self):
        self.network_class = OSMNxNetwork
        self.place_name = None
        self.network_type = "drive"
        self.mappings = []

    @beartype
    @require_arguments_not_none(
        "network_class", error_msg="Network class must be provided."
    )
    def use_network(self, network_class: NetworkBase) -> "NetworkFactory":
        self.network_class = network_class
        return self

    @beartype
    @require_arguments_not_none("place_name", error_msg="Place name must be provided.")
    def with_place(
        self, place_name: str, network_type: str = "drive"
    ) -> "NetworkFactory":
        self.place_name = place_name
        self.network_type = network_type
        return self

    @beartype
    @require_arguments_not_none(
        "mapping_type",
        "longitude_column_name",
        "latitude_column_name",
        "output_column",
        error_msg="All mapping parameters must be specified.",
    )
    def with_mapping(
        self,
        mapping_type: str,
        longitude_column_name: str,
        latitude_column_name: str,
        output_column: str,
    ) -> "NetworkFactory":
        if mapping_type not in ["node", "edge"]:
            raise ValueError("mapping_type must be 'node' or 'edge'")
        if any(mapping["output"] == output_column for mapping in self.mappings):
            raise ValueError(f"Duplicate output_column '{output_column}' detected.")
        self.mappings.append(
            {
                "type": mapping_type,
                "lon": longitude_column_name,
                "lat": latitude_column_name,
                "output": output_column,
            }
        )
        return self

    @beartype
    @require_attributes_not_none(
        "place_name", error_msg="Place name must be set before building the network."
    )
    def build(self) -> NetworkBase:
        if len(self.mappings) == 0:
            raise ValueError("At least one mapping must be set using with_mapping()")
        network = self.network_class(
            place_name=self.place_name,
            network_type=self.network_type,
            latitude_column_name=None,
            longitude_column_name=None,
        )
        network.mappings = self.mappings
        return network
