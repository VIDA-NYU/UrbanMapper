# Models

!!! tip "What is the model module?"
    The `model` module provides a simple way to cluster, classify, or run regression over given your loaded `urban data`.
    Meanwhile, we recommend to look through the [`Example`'s Model](../copy_of_examples/1-Per-Module/9-model/) for a more hands-on introduction about
    the model module and its usage.

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.model.ModelBase
    options:
        heading: "ModelBase"
        members:
            - transform
            - fit
            - predict
            - fit_predict

## ::: urban_mapper.modules.enricher.ModelFactory
    options:
        heading: "ModelFactory"
        members:
            - with_model
            - with_transform
            - with_columns
            - with_data
            - build
