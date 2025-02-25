from dependency_injector import containers, providers
import importlib
from typing import Type
from .config import MIXIN_PATHS, RAW_PIPELINE_SCHEMA


def import_class(class_path: str) -> Type:
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class AppContainer(containers.DeclarativeContainer):
    mixin_classes = providers.Dict(
        {
            mixin_name: providers.Callable(import_class, class_path)
            for mixin_name, class_path in MIXIN_PATHS.items()
        }
    )

    pipeline_schema = providers.Singleton(
        dict,
        {
            import_class(entry["class_path"]): {
                "min": entry["min"],
                "max": entry["max"],
            }
            for entry in RAW_PIPELINE_SCHEMA.values()
        },
    )


container = AppContainer()
