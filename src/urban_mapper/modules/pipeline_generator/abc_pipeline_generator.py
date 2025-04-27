from abc import ABC, abstractmethod


class PipelineGeneratorBase(ABC):
    """Abstract base class for pipeline generators.

    This class defines the interface for pipeline generators.

    !!! question "What is a pipeline geneartor's primitive"
        Pipeline generators use large language models (LLMs) to automatically
        create `UrbanMapper pipelines` from `natural language descriptions`.

    Implementations of this class must provide a `generate_urban_pipeline` method
    that takes a user description and returns Python code for an `UrbanMapper pipeline`.

    !!! note "Use of Short Name"
        The short name of the generator is used to identify the generator in the
        `PipelineGeneratorFactory`. It should be unique among all generators.

        For instance, much easier to call GPT4 than `GPT4Generator`. See further in the factory.

    Attributes:
        instructions: The instructions to guide the LLM in generating pipelines.

    Examples:
        >>> class GPT4Generator(PipelineGeneratorBase):
        ...     short_name = "GPT4"
        ...
        ...     def __init__(self, instructions: str):
        ...         self.instructions = instructions
        ...
        ...     def generate_urban_pipeline(self, user_description: str) -> str:
        ...         # Implementation that uses GPT-4 to generate a pipeline
        ...         ...
    """

    @abstractmethod
    def generate_urban_pipeline(self, user_description: str) -> str:
        """Generate an `UrbanMapper pipeline` from a `natural language description`.

        This method uses a `large language model` to generate `Python code` for an
        `UrbanMapper pipeline` based on the user's `natural language description`.
        The generated code can then be executed to create and run the pipeline.

        Args:
            user_description: A natural language description of the desired pipeline,
                such as "Load traffic data for New York and visualise accident hotspots."

        Returns:
            A string containing Python code that implements the described pipeline.
            This code can be executed with exec() to run the pipeline.

        Examples:
            >>> generator = SomeGenerator(instructions)
            >>> pipeline_code = generator.generate_urban_pipeline(
            ...     "Load taxi trip data for Manhattan and create a heatmap of pickups"
            ... )
            >>> print(pipeline_code) # You may use Ipyleaflet Code(.) for highlighting, or even `exec(pipeline_code)` for running, yet this is not recommended.
        """
        pass
