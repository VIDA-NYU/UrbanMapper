# Loaders

!!! tip "What is the loader module?"
    The `loader` module is responsible for loading geospatial data into `UrbanMapper`. 
    It provides a unified interface for loading various data formats, including `shapefiles`, `parquet`, and `CSV` files 
    with geospatial information.

    We highly recommend to look through the `User Guide`'s Loader section for a more in-depth introduction about
    the loader module and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/1-loaders.md){ .md-button } 

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.loader.LoaderBase
    options:
        heading: "LoaderBase"
        members:
            - load_data_from_file 
            - _load_data_from_file 
            - preview

## ::: urban_mapper.modules.loader.CSVLoader
    options:
        heading: "CSVLoader"
        members:
            - _load_data_from_file 
            - preview

## ::: urban_mapper.modules.loader.ParquetLoader
    options:
        heading: "ParquetLoader"
        members:
            - _load_data_from_file 
            - preview

## ::: urban_mapper.modules.loader.ShapefileLoader
    options:
        heading: "ShapefileLoader"
        members:
            - _load_data_from_file 
            - preview

## ::: urban_mapper.modules.loader.LoaderFactory
    options:
        heading: "LoaderFactory"
        members:
            - from_file 
            - from_dataframe
            - from_huggingface
            - with_columns
            - with_crs
            - with_preview
            - load
            - build
            - preview