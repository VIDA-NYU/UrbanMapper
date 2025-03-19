from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config(config_path: str = CONFIG_PATH) -> dict:
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


CONFIG = load_config()
ENRICHER_NAMESPACE = CONFIG["namespaces"]["enricher"]
DEFAULT_CRS = CONFIG["defaults"]["crs"]
MIXIN_PATHS = CONFIG["mixins"]
RAW_PIPELINE_SCHEMA = CONFIG["pipeline"]["schema"]
