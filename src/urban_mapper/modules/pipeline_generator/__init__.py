from __future__ import annotations

from typing import Any

from urban_mapper.config import (
    get_missing_optional_dependency_message,
    raise_missing_optional_dependency,
)

from .abc_pipeline_generator import PipelineGeneratorBase
from .helpers import check_openai_api_key

_MISSING_PIPELINE_GENERATOR_MESSAGE = get_missing_optional_dependency_message(
    "pipeline_generators"
)

_PIPELINE_GENERATOR_IMPORT_ERROR: Exception | None = None

try:  # pragma: no cover
    from .pipeline_generator_factory import (
        PipelineGeneratorFactory as _PipelineGeneratorFactory,
    )
except ImportError as error:  # pragma: no cover
    _PIPELINE_GENERATOR_IMPORT_ERROR = error

    class PipelineGeneratorFactory:  # type: ignore[override]
        """Placeholder factory shown when pipeline generator dependencies are missing."""

        def __init__(self, *_, **__):
            raise_missing_optional_dependency(
                "pipeline_generators", _PIPELINE_GENERATOR_IMPORT_ERROR
            )

        def __getattr__(self, _name: str) -> Any:
            raise_missing_optional_dependency(
                "pipeline_generators", _PIPELINE_GENERATOR_IMPORT_ERROR
            )

else:  # pragma: no cover
    PipelineGeneratorFactory = _PipelineGeneratorFactory

try:  # pragma: no cover
    from .generators import (
        GPT35TurboPipelineGenerator as _GPT35TurboPipelineGenerator,
        GPT4OPipelineGenerator as _GPT4OPipelineGenerator,
        GPT4PipelineGenerator as _GPT4PipelineGenerator,
    )
except ImportError as error:  # pragma: no cover
    _PIPELINE_GENERATOR_IMPORT_ERROR = _PIPELINE_GENERATOR_IMPORT_ERROR or error

    class _MissingPipelineGenerator(PipelineGeneratorBase):
        """Placeholder generator shown when LLM dependencies are missing."""

        short_name = "unavailable"

        def __init__(self, *_, **__):
            raise_missing_optional_dependency(
                "pipeline_generators", _PIPELINE_GENERATOR_IMPORT_ERROR
            )

        def generate_urban_pipeline(self, *_args: Any, **_kwargs: Any) -> str:
            raise_missing_optional_dependency(
                "pipeline_generators", _PIPELINE_GENERATOR_IMPORT_ERROR
            )

    GPT4OPipelineGenerator = _MissingPipelineGenerator  # type: ignore[assignment]
    GPT35TurboPipelineGenerator = _MissingPipelineGenerator  # type: ignore[assignment]
    GPT4PipelineGenerator = _MissingPipelineGenerator  # type: ignore[assignment]

else:  # pragma: no cover
    GPT4OPipelineGenerator = _GPT4OPipelineGenerator
    GPT35TurboPipelineGenerator = _GPT35TurboPipelineGenerator
    GPT4PipelineGenerator = _GPT4PipelineGenerator

__all__ = [
    "GPT4OPipelineGenerator",
    "GPT35TurboPipelineGenerator",
    "GPT4PipelineGenerator",
    "PipelineGeneratorBase",
    "PipelineGeneratorFactory",
    "check_openai_api_key",
]
