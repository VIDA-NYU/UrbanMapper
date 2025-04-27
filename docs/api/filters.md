# Filters

!!! tip "What is the Filter module?"
    The `filter` module is responsible for filtering geospatial datasets based on specific criteria or conditions out 
    of your `urban layer`.

    We highly recommend to look through the `User Guide`'s Filter section for a more in-depth introduction about
    the filter module and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/4-filters.md){ .md-button } 

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.filter.GeoFilterBase
    options:
        heading: "GeoFilterBase"
        members:
            - _transform 
            - transform 
            - preview

## ::: urban_mapper.modules.filter.BoundingBoxFilter
    options:
        heading: "BoundingBoxFilter"
        members:
            - _transform 
            - preview

## ::: urban_mapper.modules.filter.FilterFactory
    options:
        heading: "FilterFactory"
        members:
            - with_type 
            - transform
            - build
            - preview
            - with_preview