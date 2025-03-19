from typing import Dict, Any
from beartype import beartype
from .config import EnricherConfig
from urban_mapper.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)


@beartype
class PreviewBuilder:
    def __init__(self, config: EnricherConfig, enricher_registry: Dict[str, type]):
        self.config = config
        self.enricher_registry = enricher_registry

    def build_preview(self, format: str = "ascii") -> Any:
        if format == "ascii":
            return self._build_ascii_preview()
        elif format == "json":
            return self._build_json_preview()
        else:
            raise ValueError("Supported formats: 'ascii', 'json'")

    def _build_ascii_preview(self) -> str:
        steps = ["Enricher Workflow:", "├── Step 1: Data Input"]
        steps.append(
            f"│   ├── Group By: {', '.join(self.config.group_by) if self.config.group_by else '<Not Set>'}"
        )
        steps.append(
            f"│   └── Values From: {', '.join(self.config.values_from) if self.config.values_from else '<Not Set>'}"
        )
        steps.append("├── Step 2: Action")
        if self.config.action == "aggregate":
            method = self.config.aggregator_config.get("method", "<Not Set>")
            steps.extend(
                [
                    "│   ├── Type: Aggregate",
                    "│   ├── Aggregator: SimpleAggregator",
                    f"│   ├── Method: {method}",
                    f"│   └── Output Column: {self.config.enricher_config.get('output_column', '<Not Set>')}",
                ]
            )
        elif self.config.action == "count":
            steps.extend(
                [
                    "│   ├── Type: Count",
                    "│   ├── Aggregator: CountAggregator",
                    f"│   └── Output Column: {self.config.enricher_config.get('output_column', '<Not Set>')}",
                ]
            )
        else:
            steps.append("│   ├── Type: <Not Set>")
        steps.append("└── Step 3: Enricher")
        steps.append(f"    ├── Type: {self.config.enricher_type}")
        status = "Ready" if self._is_config_complete() else "Incomplete"
        steps.append(f"    └── Status: {status}")
        return "\n".join(steps)

    def _build_json_preview(self) -> Dict[str, Any]:
        preview_data = {
            "workflow": {
                "data_input": {
                    "group_by": self.config.group_by,
                    "values_from": self.config.values_from,
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
        return (
            bool(self.config.group_by)
            and bool(self.config.action)
            and (self.config.action != "aggregate" or bool(self.config.values_from))
            and self.config.enricher_type in self.enricher_registry
        )
