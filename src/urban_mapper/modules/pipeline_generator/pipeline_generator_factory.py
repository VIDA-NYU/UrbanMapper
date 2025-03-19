import importlib
import inspect
import pkgutil
from pathlib import Path
from thefuzz import process
from urban_mapper.modules.pipeline_generator.abc_pipeline_generator import (
    PipelineGeneratorBase,
)

DEFAULT_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"

PIPELINE_GENERATOR_REGISTRY = {}


class PipelineGeneratorFactory:
    def __init__(self):
        self._type = None
        self._custom_instructions = None

    def with_LLM(self, primitive_type: str):
        if primitive_type not in PIPELINE_GENERATOR_REGISTRY:
            available = list(PIPELINE_GENERATOR_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            suggestion = f" Maybe you meant '{match}'?" if score > 80 else ""
            raise ValueError(
                f"Unknown generator type '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self._type = primitive_type
        return self

    def with_custom_instructions(self, instructions: str):
        self._custom_instructions = instructions
        return self

    def _build(self) -> PipelineGeneratorBase:
        if self._type not in PIPELINE_GENERATOR_REGISTRY:
            raise ValueError(f"Unknown generator type: {self._type}")
        instructions = (
            self._custom_instructions or open(DEFAULT_INSTRUCTIONS_FILE, "r").read()
        )
        generator_class = PIPELINE_GENERATOR_REGISTRY[self._type]
        return generator_class(instructions)

    def generate_urban_pipeline(self, user_description: str) -> str:
        generator = self._build()
        return generator.generate_urban_pipeline(user_description)


def _initialise():
    package_dir = Path(__file__).parent / "generators"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(
                f".generators.{module_name}", package=__package__
            )
            for class_name, class_object in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(class_object, PipelineGeneratorBase)
                    and class_object is not PipelineGeneratorBase
                    and hasattr(class_object, "short_name")
                ):
                    short_name = class_object.short_name
                    if short_name in PIPELINE_GENERATOR_REGISTRY:
                        raise ValueError(
                            f"Duplicate short_name '{short_name}' in pipeline generator registry."
                        )
                    PIPELINE_GENERATOR_REGISTRY[short_name] = class_object
        except ImportError as error:
            raise ImportError(
                f"Failed to load generators module {module_name}: {error}"
            )


_initialise()
