# Enrichers

!!! tip "What is the enricher module?"
    The `enricher` module is the heart of `UrbanMapper`’s analysis—they take your `urban layer` and `transform it` into meaningful
    `statistics`, like `counting taxi pickups` at each `intersection` or `averaging building heights` per `neighborhood` given your loaded `urban data`.

    We highly recommend to look through the `User Guide`'s Enricher section for a more in-depth introduction about
    the enricher module and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/5-enrichers.md){ .md-button } 

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.enricher.EnricherBase
    options:
        heading: "EnricherBase"
        members:
            - _enrich
            - enrich
            - preview

## ::: urban_mapper.modules.enricher.SingleAggregatorEnricher
    options:
        heading: "SingleAggregatorEnricher"
        members:
            - _enrich
            - preview

## ::: urban_mapper.modules.enricher.EnricherFactory
    options:
        heading: "EnricherFactory"
        members:
            - with_data
            - with_debug
            - with_preview
            - aggregate_by
            - count_by
            - with_type
            - build
            - preview

## ::: urban_mapper.modules.enricher.BaseAggregator
    options:
        heading: "EnricherFactory"
        members:
            - _aggregate
            - aggregate

## Enricher Aggregators Functions For Faster Perusal

!!! note "In a Nutshell, How To Read That"
    An aggregation function is `name` followed by a `function` that takes a `list` of `values` and returns a single value.
    The ones below are the common we deliver, utilising mainly Pandas.

#### ::: urban_mapper.modules.enricher.AGGREGATION_FUNCTIONS

## ::: urban_mapper.modules.enricher.SimpleAggregator
    options:
        heading: "SimpleAggregator"
        members:
            - _aggregate

## ::: urban_mapper.modules.enricher.CountAggregator
    options:
        heading: "CountAggregator"
        members:
            - _aggregate
