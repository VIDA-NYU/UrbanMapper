# Auctus Mixin

!!! note "Optional module"
    Install the `auctus_mixins` extra to enable these features:

    - `pip install urban-mapper[auctus_mixins]`
    - `uv add urban-mapper --group auctus_mixins`

!!! tip "What is Auctus Mixin?"
    The `Auctus` mixin is responsible to deliver access to Auctus Dataset Search API services via the `UrbanMapper`
    workflow. It provides a set of methods to search for datasets, get dataset details, and download datasets.

    A mixin, in this very instance, is nothing more than a class that connects external libraries for their use
    directly adapted towards the `UrbanMapper` workflow.

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

::: urban_mapper.mixins.auctus
