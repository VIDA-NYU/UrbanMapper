from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, TypeVar, cast


@dataclass(frozen=True)
class OptionalDependencyInfo:
    """Metadata Helper showing to users how to install an optional dependency group"""

    extra: str
    description: str

    def missing_message(self) -> str:
        pip_command = f"pip install urban-mapper[{self.extra}]"
        uv_command = f"uv add urban-mapper --group {self.extra}"
        return (
            f"{self.description} Install them with `{pip_command}` or `{uv_command}`."
        )


OPTIONAL_DEPENDENCIES: Dict[str, OptionalDependencyInfo] = {
    "auctus_mixins": OptionalDependencyInfo(
        extra="auctus_mixins",
        description="Auctus mixins require the optional `auctus-search` dependency.",
    ),
    "interactive_table_vis": OptionalDependencyInfo(
        extra="interactive_table_vis",
        description="Interactive table visualisations require the optional Skrub dependency.",
    ),
    "jupytergis_mixins": OptionalDependencyInfo(
        extra="jupytergis_mixins",
        description="JupyterGIS features require the optional `jupytergis` dependencies.",
    ),
    "pipeline_generators": OptionalDependencyInfo(
        extra="pipeline_generators",
        description="Pipeline generators require optional LLM dependencies.",
    ),
}


def get_missing_optional_dependency_message(extra_key: str) -> str:
    try:
        return OPTIONAL_DEPENDENCIES[extra_key].missing_message()
    except KeyError as error:
        raise KeyError(f"Unknown optional dependency group: {extra_key}") from error


def raise_missing_optional_dependency(
    extra_key: str, error: Exception | None = None
) -> None:
    message = get_missing_optional_dependency_message(extra_key)
    if error is None:
        raise ModuleNotFoundError(message)
    raise ModuleNotFoundError(message) from error


F = TypeVar("F", bound=Callable[..., Any])


def optional_dependency_required(
    extra_key: str,
    available: Callable[[], bool],
    import_error_supplier: Callable[[], Exception | None] | None = None,
) -> Callable[[F], F]:
    """Decorator helper ensuring an optional dependency group is installed before use

    Args:
        extra_key: Key of the optional dependency group defined in OPTIONAL_DEPENDENCIES.
        available: Callable returning True when the dependency group is available.
        import_error_supplier: Optional callable returning the most recent
            import error for the dependency group. When provided, the raised
            ModuleNotFoundError will chain this error for additional
            context.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            if not available():
                import_error = (
                    import_error_supplier() if import_error_supplier else None
                )
                raise_missing_optional_dependency(extra_key, import_error)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
