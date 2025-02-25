from typing import Type, Dict
from beartype import beartype
from osmnx_mapping.modules.preprocessing.imputer import GeoImputerBase
from osmnx_mapping.modules.preprocessing.filters import GeoFilterBase

IMPUTER_REGISTRY: Dict[str, Type[GeoImputerBase]] = {}
FILTER_REGISTRY: Dict[str, Type[GeoFilterBase]] = {}


@beartype
def register_imputer(name: str, imputer_class: Type[GeoImputerBase]) -> None:
    if not issubclass(imputer_class, GeoImputerBase):
        raise TypeError
    IMPUTER_REGISTRY[name] = imputer_class


@beartype
def register_filter(name: str, filter_class: Type[GeoFilterBase]) -> None:
    if not issubclass(filter_class, GeoFilterBase):
        raise TypeError
    FILTER_REGISTRY[name] = filter_class
