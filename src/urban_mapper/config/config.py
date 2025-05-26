"""
Configuration management module for UrbanMapper.

This module handles loading and parsing of the main configuration file (config.yaml)
which defines system-wide settings including:

- Default coordinate reference systems
- Mixin class mappings for the plugin architecture
- Namespace configurations for different modules
- Pipeline schema definitions
- Enricher and other component configurations

The configuration is loaded once at module import and provides constants
used throughout the UrbanMapper system.

Configuration Structure:
    defaults:
        crs: Default coordinate reference system (e.g., "EPSG:4326")
    mixins:
        Mapping of mixin names to their implementation classes
    namespaces:
        enricher: Namespace configuration for enricher components
    pipeline:
        schema: Pipeline configuration schema definition

Example:
    >>> from urban_mapper.config import DEFAULT_CRS, CONFIG
    >>> print(f"Default CRS: {DEFAULT_CRS}")
    >>> print(f"Available mixins: {list(CONFIG['mixins'].keys())}")
"""

from pathlib import Path
import yaml
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config(config_path: str = CONFIG_PATH) -> Dict[str, Any]:
    """
    Load and parse the UrbanMapper configuration file.

    This function reads the main configuration YAML file and returns its contents
    as a dictionary. The configuration includes system defaults, mixin mappings,
    namespace settings, and pipeline schemas.

    Args:
        config_path: Path to the configuration YAML file. Defaults to the
            standard config.yaml location in the package.

    Returns:
        Dictionary containing the parsed configuration with keys like:
        - 'defaults': System default values (CRS, etc.)
        - 'mixins': Mixin class mapping for plugin architecture
        - 'namespaces': Module namespace configurations
        - 'pipeline': Pipeline schema definitions

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If the configuration file contains invalid YAML.

    Example:
        >>> config = load_config()
        >>> default_crs = config['defaults']['crs']
        >>> available_mixins = list(config['mixins'].keys())
    """
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


CONFIG = load_config()
ENRICHER_NAMESPACE = CONFIG["namespaces"]["enricher"]
DEFAULT_CRS = CONFIG["defaults"]["crs"]
MIXIN_PATHS = CONFIG["mixins"]
RAW_PIPELINE_SCHEMA = CONFIG["pipeline"]["schema"]
