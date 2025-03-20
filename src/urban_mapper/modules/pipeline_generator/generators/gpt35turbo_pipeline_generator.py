import ell

from urban_mapper.modules.pipeline_generator.helpers.check_openai_api_key import (
    check_openai_api_key,
)
from urban_mapper.modules.pipeline_generator.abc_pipeline_generator import (
    PipelineGeneratorBase,
)


class GPT35TurboPipelineGenerator(PipelineGeneratorBase):
    short_name = "gpt-3.5-turbo"

    def __init__(self, instructions: str):
        self.instructions = instructions

    @check_openai_api_key
    def generate_urban_pipeline(self, user_description: str) -> str:
        @ell.simple(model="gpt-3.5-turbo")
        def generate_code():
            return f"{self.instructions}\n\nUser Description: {user_description}\n\nGenerate the Python code for the UrbanPipeline:"

        return generate_code()
