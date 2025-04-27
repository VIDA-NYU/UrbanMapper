# Pipeline Generators

!!! tip "What is the Pipeline Generator module?"
    The `Pipeline Generator` module is solving the following scenario, imagine telling `UrbanMapper` exactly what 
    urban analysis you want, and watching it craft a pipeline for you—no coding required. Powered by 
    `Large Language Models (LLMs)`, this module transforms your natural language descriptions into executable 
    Python code for `UrbanMapper` pipelines.

    We highly recommend to look through the `User Guide`'s Pipeline generator section for a more in-depth introduction about
    the pipeline generator module and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/8-pipeline-generators.md){ .md-button }

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.pipeline_generator.PipelineGeneratorBase
    options:
        heading: "PipelineGeneratorBase"
        members:
            - generate_urban_pipeline 

## ::: urban_mapper.modules.pipeline_generator.GPT4PipelineGenerator
    options:
        heading: "GPT4PipelineGenerator"
        members:
            - generate_urban_pipeline 

## ::: urban_mapper.modules.pipeline_generator.GPT4OPipelineGenerator
    options:
        heading: "GPT4OPipelineGenerator"
        members:
            - generate_urban_pipeline 

## ::: urban_mapper.modules.pipeline_generator.GPT35TurboPipelineGenerator
    options:
        heading: "GPT35TurboPipelineGenerator"
        members:
            - generate_urban_pipeline 

## ::: urban_mapper.modules.pipeline_generator.PipelineGeneratorFactory
    options:
        heading: "PipelineGeneratorFactory"
        members:
            - with_LLM
            - with_custom_instructions
            - generate_urban_pipeline