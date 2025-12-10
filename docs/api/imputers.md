# Imputers

!!! tip "What is the Imputer module?"
    The `imputer` module is responsible for handling missing data in geospatial datasets, dealing with missing information of latitude-longitude data columns or geometry specified in [WKT format](https://libgeos.org/specifications/wkt/).

    Meanwhile, we recommend to look through the [`Example`'s Imputer](../copy_of_examples/1-Per-Module/3-imputer/) for a more hands-on introduction about
    the Imputer module and its usage.

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.imputer.GeoImputerBase
    options:
        heading: "GeoImputerBase"
        members:
            - _transform 
            - transform 
            - preview

## ::: urban_mapper.modules.imputer.SimpleGeoImputer
    options:
        heading: "SimpleGeoImputer"
        members:
            - _transform 
            - preview


## ::: urban_mapper.modules.imputer.AddressGeoImputer
    options:
        heading: "AddressGeoImputer"
        members:
            - _transform 
            - preview

## ::: urban_mapper.modules.imputer.ImputerFactory
    options:
        heading: "ImputerFactory"
        members:
            - with_type 
            - on_columns
            - transform
            - build
            - preview
            - with_preview