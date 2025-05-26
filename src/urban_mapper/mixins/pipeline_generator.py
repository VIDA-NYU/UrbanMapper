from urban_mapper.modules.pipeline_generator.pipeline_generator_factory import (
    PipelineGeneratorFactory,
)


class PipelineGeneratorMixin(PipelineGeneratorFactory):
    """
    Mixin providing access to AI-powered pipeline generation through the UrbanMapper interface.

    This class extends PipelineGeneratorFactory to provide seamless integration of
    automated pipeline generation capabilities within the UrbanMapper ecosystem.
    It enables users to generate complete data analysis pipelines using natural
    language descriptions and AI models like GPT-4.

    The mixin pattern allows UrbanMapper to compose AI functionality alongside
    other components while maintaining a clean, unified API for pipeline creation.

    Inherits all methods from PipelineGeneratorFactory, including:
        - gpt4o(): Generate pipelines using GPT-4 Optimized model
        - gpt4(): Generate pipelines using GPT-4 model  
        - gpt35turbo(): Generate pipelines using GPT-3.5 Turbo model
        - preview(): Preview available pipeline generators

    Example:
        >>> import os
        >>> os.environ['OPENAI_API_KEY'] = 'your-api-key'
        >>> mapper = UrbanMapper()
        >>> # Generate a pipeline from natural language
        >>> pipeline = mapper.pipeline_generator.gpt4o(
        ...     task_description="Analyze NYC taxi trips and find patterns in high-tip areas",
        ...     data_description="CSV file with pickup/dropoff coordinates and fare amounts"
        ... )
        >>> # Execute the generated pipeline
        >>> results = pipeline.run(data_path='taxi_trips.csv')

    Note:
        Requires OpenAI API key to be set in environment variables.
        Different models have varying capabilities and response times.

    See Also:
        PipelineGeneratorFactory: The underlying factory class
        PipelineGeneratorBase: Abstract base class for all generators
        UrbanPipeline: Pipeline execution and orchestration
    """

    def __init__(self):
        super().__init__()
