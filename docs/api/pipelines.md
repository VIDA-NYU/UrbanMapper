# Pipeline

!!! tip "What is the pipeline tool?"
    The `pipeline` tool is a module that allows you to create a sequence of data processing steps, or "pipeline", 
    to transform your `urban layer` given your `urban dataset` and some user-defined `enrichments`.

    We highly recommend to look through the `User Guide`'s Pipeline section for a more in-depth introduction about
    the pipeline tool and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/7-pipelines.md){ .md-button } 

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.pipeline.UrbanPipeline
    options:
        heading: "UrbanPipeline"
        members:
            - named_steps
            - get_step_names
            - get_step
            - compose
            - transform
            - compose_transform
            - visualise
            - save
            - load
            - __getitem__
            - preview
            - to_jgis


## ::: urban_mapper.pipeline.PipelineExecutor
    options:
        heading: "PipelineExecutor"
        members:
            - compose
            - transform
            - compose_transform
            - visualise

## ::: urban_mapper.pipeline.PipelineValidator
    options:
        heading: "PipelineValidator"
        members:
            - _validate_steps
