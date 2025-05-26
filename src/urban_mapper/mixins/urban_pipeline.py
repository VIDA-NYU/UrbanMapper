from urban_mapper.pipeline import UrbanPipeline


class UrbanPipelineMixin(UrbanPipeline):
    """
    Mixin providing access to pipeline execution functionality through the UrbanMapper interface.

    This class extends UrbanPipeline to provide seamless integration of pipeline
    orchestration and execution capabilities within the UrbanMapper ecosystem.
    It enables users to create, configure, and execute complex data processing
    workflows that combine multiple UrbanMapper components.

    The mixin pattern allows UrbanMapper to compose pipeline functionality alongside
    other components while maintaining a unified API for workflow management.

    Inherits all methods from UrbanPipeline, including:
        - add_step(): Add processing steps to the pipeline
        - run(): Execute the complete pipeline
        - to_json(): Serialize pipeline configuration
        - from_json(): Load pipeline from configuration
        - validate(): Validate pipeline configuration

    Example:
        >>> mapper = UrbanMapper()
        >>> # Create a new pipeline
        >>> pipeline = mapper.urban_pipeline
        >>> # Add processing steps
        >>> pipeline.add_step('loader', 'csv', {'file_path': 'data.csv'})
        >>> pipeline.add_step('enricher', 'osm_features', {'aggregator': 'count'})
        >>> pipeline.add_step('visualiser', 'interactive', {'color_column': 'osm_count'})
        >>> # Execute the pipeline
        >>> results = pipeline.run()

    See Also:
        UrbanPipeline: The underlying pipeline class providing execution logic
        PipelineGenerator: AI-powered pipeline creation
        UrbanMapper: Main interface for accessing all components
    """

    def __init__(self):
        super().__init__()
