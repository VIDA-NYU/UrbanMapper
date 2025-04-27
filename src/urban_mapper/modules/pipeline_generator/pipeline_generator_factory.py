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
    """Factory class for creating and configuring pipeline generators.
    
    This class implements a fluent chaining-methods-based interface for creating and configuring pipeline
    generators. `Pipeline generators` use `Large Language Models (LLMs)` to automatically create `UrbanMapper pipelines`
    from natural language descriptions.
    
    The factory manages the details of `generator instantiation`, `configuration`, and
    `execution`, providing a consistent interface regardless of the underlying LLM implementation.
    
    Attributes:
        _type: The type of LLM-based generator to create.
        _custom_instructions: Optional custom instructions to guide the LLM.
        
    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> pipeline_code = mapper.pipeline_generator.with_LLM("GPT4")\
        ...     .generate_urban_pipeline(
        ...         "Load taxi trips in Manhattan and show the count of pickups per street segments (roads)."
        ...     )
    """

    def __init__(self):
        self._type = None
        self._custom_instructions = None

    def with_LLM(self, primitive_type: str) -> "PipelineGeneratorFactory":
        """Specify the LLM to use for pipeline generation.

        !!! note "See This As `with.type(.)`"
            In mostly all other modules we use `with.type(.)` to specify the type of
            primitive given the module we are trying to use. Here we name it `with_LLM`
            for the sake of clarity and given the very little scope the current module has.

        This method sets the type of LLM to use for generating pipelines. Available
        types are registered in the `PIPELINE_GENERATOR_REGISTRY` or simply by perusing the folder
        `generators` in `src/urban_mapper/modules/pipeline_generator/`, they are all
        subclasses of `PipelineGeneratorBase`. The short name of the generator is used
        to identify the generator in the factory. It should be unique among all generators.

        !!! warning "Naming Mistakes"
            If you make a mistake in the name of the generator, the factory will
            provide a probable suggestion based on the available names. This is done using
            the `fuzzywuzzy` library, which uses Levenshtein distance to find the closest match.

            Pretty cool addition to `UrbanMapper`!

        Args:
            primitive_type: The name of the LLM type to use, such as "GPT4" or "GPT35Turbo".

        Returns:
            The PipelineGeneratorFactory instance for method chaining.

        Raises:
            ValueError: If the specified LLM type is not found in the registry.

        Examples:
            >>> generator = mapper.pipeline_generator.with_LLM("GPT4")
        """
        if primitive_type not in PIPELINE_GENERATOR_REGISTRY:
            available = list(PIPELINE_GENERATOR_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            suggestion = f" Maybe you meant '{match}'?" if score > 80 else ""
            raise ValueError(
                f"Unknown generator type '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self._type = primitive_type
        return self

    def with_custom_instructions(self, instructions: str) -> "PipelineGeneratorFactory":
        """Set custom instructions for guiding the LLM.

        This method provides custom instructions to guide the LLM in generating
        pipelines. This can be used to override the default instructions or to
        provide additional context or constraints.

        !!! question "What is the default instructions file?"
            The default instructions file is located in: `src/urban_mapper/modules/pipeline_generator/instructions.txt`.

        Args:
            instructions: The custom instructions to provide to the LLM.

        Returns:
            The PipelineGeneratorFactory instance for method chaining.

        Examples:
            >>> instructions = "Generate a pipeline that focuses on urban mobility..."
            >>> generator = mapper.pipeline_generator.with_custom_instructions(instructions)

            >>> # Using a file reading
            >>> with open("path/to/custom_instructions.txt", "r") as file:
            ...     instructions = file.read()
            >>> generator = mapper.pipeline_generator.with_custom_instructions(instructions)
        """
        self._custom_instructions = instructions
        return self

    def _build(self) -> PipelineGeneratorBase:
        """Build and return the configured pipeline generator instance.

        This method finalises the configuration and instantiates the appropriate
        pipeline generator implementation. It's an internal method used by
        the generate_urban_pipeline method.

        Returns:
            An instance of a class derived from PipelineGeneratorBase, configured
            according to the settings specified through the factory methods.

        Raises:
            ValueError: If the LLM type is not specified or is invalid.
        """
        if self._type not in PIPELINE_GENERATOR_REGISTRY:
            raise ValueError(f"Unknown generator type: {self._type}")
        instructions = (
            self._custom_instructions or open(DEFAULT_INSTRUCTIONS_FILE, "r").read()
        )
        generator_class = PIPELINE_GENERATOR_REGISTRY[self._type]
        return generator_class(instructions)

    def generate_urban_pipeline(self, user_description: str) -> str:
        """Generate an `UrbanMapper pipeline` suggestion from a `natural language description`.
        
        This method uses the configured LLM to generate Python code for an
        `UrbanMapper pipeline` based on the user's `natural language description`.
        The generated code can then be executed to create and run the pipeline.
        
        Args:
            user_description: A natural language description of the desired pipeline,
                such as "Load traffic data for New York and visualise accident hotspots."
                
        Returns:
            A string containing Python code that implements the described pipeline.
            This code can be executed with exec() to run the pipeline.
            
        Examples:
            >>> pipeline_code = PipelineGeneratorFactory().with_LLM("GPT4")\
            ...     .generate_urban_pipeline(
            ...         "Load taxi trip data for Manhattan and create a heatmap of pickups"
            ...     )
        """
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
