from typing import Optional, Dict, Any, Type, Union
import importlib
import inspect
import pkgutil
from pathlib import Path
from beartype import beartype
from osmnx_mapping.modules.preprocessing.imputer import GeoImputerBase
from osmnx_mapping.modules.preprocessing.filters import GeoFilterBase
from osmnx_mapping.modules.preprocessing.factory.registries import (
    IMPUTER_REGISTRY,
    FILTER_REGISTRY,
    register_imputer,
    register_filter,
)
from osmnx_mapping.utils.helpers import require_single_attribute_value

NAMESPACE = "osmnx_mapping.modules"
IMPUTER_PATH = f"{NAMESPACE}.preprocessing.imputer.imputers"
FILTER_PATH = f"{NAMESPACE}.preprocessing.filters.filters"


class PreprocessingFactory:
    def __init__(self) -> None:
        self._preprocessor_type: Optional[str] = None
        self._config: Dict[str, Any] = {}

    @require_single_attribute_value(
        attr_name="_preprocessor_type",
        param_name="imputer_type",
        error_msg="Cannot set '{new}' after '{current}'. Only one preprocessor type is allowed per instance.",
    )
    @beartype
    def with_imputer(
        self,
        imputer_type: str,
        latitude_column_name: str,
        longitude_column_name: str,
        **extra_params: Any,
    ) -> "PreprocessingFactory":
        self._preprocessor_type = imputer_type
        self._config = {
            "latitude_column_name": latitude_column_name,
            "longitude_column_name": longitude_column_name,
            **extra_params,
        }
        return self

    @require_single_attribute_value(
        attr_name="_preprocessor_type",
        param_name="filter_type",
        error_msg="Cannot set '{new}' after '{current}'. Only one preprocessor type is allowed per instance.",
    )
    @beartype
    def with_filter(
        self,
        filter_type: str,
        **extra_params: Any,
    ) -> "PreprocessingFactory":
        self._preprocessor_type = filter_type
        self._config = extra_params
        return self

    @beartype
    def build(self) -> Union[GeoImputerBase, GeoFilterBase]:
        if not self._preprocessor_type:
            raise ValueError(
                "No preprocessor type specified. Use with_imputer() or with_filter()."
            )

        if self._preprocessor_type in IMPUTER_REGISTRY:
            if (
                "latitude_column_name" not in self._config
                or "longitude_column_name" not in self._config
            ):
                raise ValueError("Missing latitude/longitude columns for imputer.")
            preprocessor_class = self._get_imputer_class(self._preprocessor_type)
        elif self._preprocessor_type in FILTER_REGISTRY:
            preprocessor_class = self._get_filter_class(self._preprocessor_type)
        else:
            raise ValueError(
                f"Unknown preprocessor type '{self._preprocessor_type}'. "
                f"Available: {list(IMPUTER_REGISTRY.keys()) + list(FILTER_REGISTRY.keys())}."
            )

        return preprocessor_class(**self._config)

    @beartype
    def _get_imputer_class(self, imputer_type: str) -> Type[GeoImputerBase]:
        if imputer_type not in IMPUTER_REGISTRY:
            raise ValueError(
                f"Unknown imputer type '{imputer_type}'. Available: {list(IMPUTER_REGISTRY.keys())}."
            )
        return IMPUTER_REGISTRY[imputer_type]

    @beartype
    def _get_filter_class(self, filter_type: str) -> Type[GeoFilterBase]:
        if filter_type not in FILTER_REGISTRY:
            raise ValueError(
                f"Unknown filter type '{filter_type}'. Available: {list(FILTER_REGISTRY.keys())}."
            )
        return FILTER_REGISTRY[filter_type]

    @classmethod
    def _initialise(cls) -> None:
        for path, registry, base_class in [
            (
                Path(__file__).parent / "imputer/imputers",
                IMPUTER_REGISTRY,
                GeoImputerBase,
            ),
            (Path(__file__).parent / "filters/filters", FILTER_REGISTRY, GeoFilterBase),
        ]:
            for _, module_name, _ in pkgutil.iter_modules([str(path)]):
                try:
                    module_path = (
                        IMPUTER_PATH if base_class == GeoImputerBase else FILTER_PATH
                    )
                    module = importlib.import_module(f"{module_path}.{module_name}")
                    for class_name, class_object in inspect.getmembers(
                        module, inspect.isclass
                    ):
                        if (
                            issubclass(class_object, base_class)
                            and class_object is not base_class
                            and class_name not in registry
                        ):
                            register_func = (
                                register_imputer
                                if base_class == GeoImputerBase
                                else register_filter
                            )
                            register_func(class_name, class_object)
                except ImportError as error:
                    print(f"Warning: Failed to load module {module_name}: {error}")


PreprocessingFactory._initialise()
