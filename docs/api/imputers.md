# Imputers

!!! tip "What is the Imputer module?"
    The `imputer` module is responsible for handling missing data in geospatial datasets.

    We highly recommend to look through the `User Guide`'s Imputer section for a more in-depth introduction about
    the imputer module and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/3-imputers.md){ .md-button } 

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