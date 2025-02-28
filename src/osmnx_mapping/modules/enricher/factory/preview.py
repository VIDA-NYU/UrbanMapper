from typing import Dict
from beartype import beartype
from .config import EnricherConfig
from osmnx_mapping.modules.enricher.abc_enricher import EnricherBase
from osmnx_mapping.modules.enricher.aggregator.aggregators.simple_aggregator import (
    AGGREGATION_FUNCTIONS,
)


class PreviewBuilder:
    def __init__(self, config: EnricherConfig, enricher_registry: Dict[str, type]):
        self.config = config
        self.enricher_registry = enricher_registry
        self.edge_methods = EnricherBase.EDGE_METHODS

    @beartype
    def build_preview(self, format: str = "ascii") -> str:
        if format == "ascii":
            return self._build_ascii_preview()
        elif format == "json":
            return self._build_json_preview()
        else:
            raise ValueError("Supported formats: 'ascii', 'json'")

    def _build_ascii_preview(self) -> str:
        steps = ["Enricher Pipeline Preview:", "├── Step 1: Data Input"]

        if self.config.group_by:
            steps.append(f"│   ├── Group By: {', '.join(self.config.group_by)}")
        else:
            steps.append("│   ├── Group By: <Not Set> (Required)")
        steps.append(
            f"│   └── Values From: {', '.join(self.config.values_from) if self.config.values_from else '<Not Set>'} "
            "(Optional, required for aggregation)"
        )

        steps.append("├── Step 2: Action")
        if self.config.action:
            if self.config.action == "aggregate":
                method = self.config.aggregator_config.get("method", "<Not Set>")
                target = self.config.enricher_config.get("target", "<Not Set>")
                steps.extend(
                    [
                        "│   ├── Type: Aggregate",
                        "│   ├── Aggregator: SimpleAggregator",
                        f"│   ├── Method: {method} (Available: {', '.join(AGGREGATION_FUNCTIONS.keys())})",
                        f"│   ├── Edge Method: {self.config.enricher_config.get('edge_method', '<Not Set>')} "
                        f"(Available: {', '.join(self.edge_methods.keys())})",
                        f"│   ├── Target: {target}",
                        f"│   └── Output Column: {self.config.enricher_config.get('output_column', '<Not Set>')}",
                    ]
                )
            elif self.config.action == "count":
                target = self.config.enricher_config.get("target", "<Not Set>")
                steps.extend(
                    [
                        "│   ├── Type: Count",
                        "│   ├── Aggregator: CountAggregator",
                        f"│   ├── Edge Method: {self.config.enricher_config.get('edge_method', '<Not Set>')} "
                        f"(Available: {', '.join(self.edge_methods.keys())})",
                        f"│   ├── Target: {target}",
                        f"│   └── Output Column: {self.config.enricher_config.get('output_column', '<Not Set>')}",
                    ]
                )
        else:
            steps.append("│   ├── Type: <Not Set> (Use aggregate_with() or count_by())")

        steps.append("└── Step 3: Enricher")
        enricher_type = self.config.enricher_type
        steps.append(f"    ├── Type: {enricher_type}")
        status = "Ready" if self._is_config_complete() else "Incomplete"
        steps.append(f"    └── Status: {status} ({self._get_status_details()})")

        return "\n".join(steps)

    def _build_json_preview(self) -> str:
        import json

        preview_data = {
            "pipeline": {
                "data_input": {
                    "group_by": self.config.group_by,
                    "values_from": self.config.values_from,
                },
                "action": {
                    "type": self.config.action,
                    "aggregator_config": self.config.aggregator_config,
                    "enricher_config": self.config.enricher_config,
                },
                "enricher": {
                    "type": self.config.enricher_type,
                    "status": "ready" if self._is_config_complete() else "incomplete",
                },
            },
            "metadata": {
                "available_aggregation_methods": list(AGGREGATION_FUNCTIONS.keys()),
                "available_edge_methods": list(self.edge_methods.keys()),
                "available_enrichers": list(self.enricher_registry.keys()),
            },
        }
        return json.dumps(preview_data, indent=2)

    def _is_config_complete(self) -> bool:
        return (
            bool(self.config.group_by)
            and bool(self.config.action)
            and (self.config.action != "aggregate" or bool(self.config.values_from))
            and self.config.enricher_type in self.enricher_registry
        )

    def _get_status_details(self) -> str:
        issues = []
        if not self.config.group_by:
            issues.append("group_by missing")
        if not self.config.action:
            issues.append("action missing")
        if self.config.action == "aggregate" and not self.config.values_from:
            issues.append("values_from missing for aggregation")
        if self.config.enricher_type not in self.enricher_registry:
            issues.append(f"enricher type '{self.config.enricher_type}' not registered")
        return (
            "All required parameters set"
            if not issues
            else f"Missing: {', '.join(issues)}"
        )
