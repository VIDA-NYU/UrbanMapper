# Filters

!!! tip "What is the Filter module?"
    The `filter` module is responsible for filtering geospatial datasets based on specific criteria or conditions out 
    of your `urban layer` and based on information of latitude-longitude data columns or geometry specified in [WKT format](https://libgeos.org/specifications/wkt/).

    Meanwhile, we recommend to look through the [`Example`'s Filter](../copy_of_examples/1-Per-Module/4-filter/) for a more hands-on introduction about
    the Filter module and its usage.


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