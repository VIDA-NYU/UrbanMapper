from typing import Dict, Any
from beartype import beartype
from .config import EnricherConfig
from urban_mapper.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)


@beartype
class PreviewBuilder:
    """Builder For Previews of Enricher Configurations.

    Generates readable previews of enricher setups—great for debugging / docs / sharing.

    Attributes:
        config: Enricher config to preview.
        enricher_registry: Registry of enricher types.
    """

    def __init__(self, config: EnricherConfig, enricher_registry: Dict[str, type]):
        self.config = config
        self.enricher_registry = enricher_registry

    def build_preview(self, format: str = "ascii") -> Any:
        """Build a preview in the specified format.

        Args:
            format: "ascii" for text, "json" for a dict.

        Returns:
            String for "ascii", dict for "json".

        Raises:
            ValueError: If format isn’t "ascii" or "json".

        Examples:
            >>> import urban_mapper as um
            >>> mapper = um.UrbanMapper()
            >>> enricher = mapper.enricher\
            ...     .with_data(group_by="street")\
            ...     .count_by()\
            ...     .build()
            >>> enricher.preview()
        """
        if format == "ascii":
            return self._build_ascii_preview()
        elif format == "json":
            return self._build_json_preview()
        else:
            raise ValueError("Supported formats: 'ascii', 'json'")

    def _build_ascii_preview(self) -> str:
        """Build an ASCII text preview of the enricher configuration.

        This method creates a human-readable tree representation of the enricher
        configuration, showing the data input, action (aggregate or count),
        and enricher type, along with their settings.

        Returns:
            A string containing the ASCII preview.
        """
        steps = ["Enricher Workflow:", "├── Step 1: Data Input"]
        steps.append(
            f"│   ├── Group By: {', '.join(self.config.group_by) if self.config.group_by else '<Not Set>'}"
        )
        steps.append(
            f"│   └── Values From: {', '.join(self.config.values_from) if self.config.values_from else '<Not Set>'}"
        )
        if self.config.data_id:
            steps.append(f"│   └── Data ID: {self.config.data_id}")
        steps.append("├── Step 2: Action")
        if self.config.action == "aggregate":
            method = self.config.aggregator_config.get("method")
            method_display = (
                method
                if isinstance(method, str)
                else (method.__name__ if hasattr(method, "__name__") else "custom")
            )
            steps.extend(
                [
                    "│   ├── Type: Aggregate",
                    "│   ├── Aggregator: SimpleAggregator",
                    f"│   ├── Method: {method_display}",
                    f"│   └── Output Column: {self.config.enricher_config.get('output_column', '<Not Set>')}",
                ]
            )
        elif self.config.action == "count":
            steps.extend(
                [
                    "│   ├── Type: Count",
                    "│   ├── Aggregator: CountAggregator",
                    f"│   └── Output Column: {self.config.enricher_config.get('output_column', 'count')}",
                ]
            )
        steps.append("└── Step 3: Enricher")
        steps.append(f"    ├── Type: {self.config.enricher_type}")
        status = "Ready" if self._is_config_complete() else "Incomplete"
        steps.append(f"    └── Status: {status}")
        return "\n".join(steps)

    def _build_json_preview(self) -> Dict[str, Any]:
        """Build a JSON preview of the enricher configuration.

        This method creates a machine-readable dictionary representation of the
        enricher configuration, suitable for programmatic processing or serialization
        to JSON. It includes all the configuration details as well as metadata
        about available options.

        Returns:
            A dictionary containing the preview data.
        """
        preview_data = {
            "workflow": {
                "data_input": {
                    "group_by": self.config.group_by,
                    "values_from": self.config.values_from,
                    "data_id": self.config.data_id,
                },
                "action": {
                    "type": self.config.action,
                    "aggregator_config": self.config.aggregator_config,
                    "enricher_config": self.config.enricher_config,
                },
                "enricher": {"type": self.config.enricher_type},
            },
            "metadata": {
                "available_aggregation_methods": list(AGGREGATION_FUNCTIONS.keys())
            },
        }
        return preview_data

    def _is_config_complete(self) -> bool:
        """Check if the enricher configuration is complete and ready to use.

        This method validates that all required fields are set in the configuration,
        depending on the action type. For example, aggregate actions require
        values_from to be set, while all actions require group_by.

        Returns:
            True if the configuration is complete, False otherwise.
        """
        return (
            bool(self.config.group_by)
            and bool(self.config.action)
            and (self.config.action != "aggregate" or bool(self.config.values_from))
            and self.config.enricher_type in self.enricher_registry
        )
