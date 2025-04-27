import ell

from urban_mapper.modules.pipeline_generator.helpers.check_openai_api_key import (
    check_openai_api_key,
)
from urban_mapper.modules.pipeline_generator.abc_pipeline_generator import (
    PipelineGeneratorBase,
)


class GPT4PipelineGenerator(PipelineGeneratorBase):
    """Generates `UrbanMapper pipelines` using GPT-4.

    This class uses the GPT-4 language model via the `ell` library to generate
    Python code for `UrbanMapper pipelines` based on user-provided instructions and descriptions.

    !!! question "What is `ell`"
        `ell` is a lightweight, functional prompt engineering framework built on a few core principles:

        - [x] Prompts are programs, not strings.
        - [x] Prompts are actually parameters of a machine learning model.
        - [x] Tools for monitoring, versioning, and visualization
        - [x] Multimodality should be first class
        - [x] ...and much more!

        See more in [ell github repository](in https://github.com/MadcowD/ell).

    !!! note "Short Name"
        To use this primitive, when calling `with_LLM(.)` make sure to write `gpt-4` as the short name.
    """

    short_name = "gpt-4"

    def __init__(self, instructions: str):
        self.instructions = instructions

    @check_openai_api_key
    def generate_urban_pipeline(self, user_description: str) -> str:
        @ell.simple(model="gpt-4")
        def generate_code():
            return f"{self.instructions}\n\nUser Description: {user_description}\n\nGenerate the Python code for the UrbanPipeline:"

        return generate_code()
