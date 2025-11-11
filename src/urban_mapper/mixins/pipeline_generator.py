from __future__ import annotations

from urban_mapper.config import (
    get_missing_optional_dependency_message,
    raise_missing_optional_dependency,
)

_MISSING_PIPELINE_GENERATOR_MESSAGE = get_missing_optional_dependency_message(
    "pipeline_generators"
)

try:  # pragma: no cover
    from urban_mapper.modules.pipeline_generator.pipeline_generator_factory import (
        PipelineGeneratorFactory,
    )
except ImportError as error:  # pragma: no cover
    _PIPELINE_GENERATORS_AVAILABLE = False
    _PIPELINE_GENERATOR_IMPORT_ERROR = error

    class PipelineGeneratorMixin:
        """Placeholder mixin shown when pipeline generator dependencies are missing."""

        def __init__(self, *_, **__):
            raise_missing_optional_dependency(
                "pipeline_generators", _PIPELINE_GENERATOR_IMPORT_ERROR
            )

else:  # pragma: no cover
    _PIPELINE_GENERATORS_AVAILABLE = True
    _PIPELINE_GENERATOR_IMPORT_ERROR = None

    class PipelineGeneratorMixin(PipelineGeneratorFactory):
        def __init__(self) -> None:
            super().__init__()
