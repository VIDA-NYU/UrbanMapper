from urban_mapper.modules.pipeline_generator.pipeline_generator_factory import (
    PipelineGeneratorFactory,
)


class PipelineGeneratorMixin(PipelineGeneratorFactory):
    def __init__(self):
        super().__init__()
