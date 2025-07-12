# Loaders

!!! tip "What is the loader module?"
    The `loader` module is responsible for loading geospatial data into `UrbanMapper`. 
    It provides a unified interface for loading various data formats, including `shapefiles`, `parquet`, and `CSV` files 
    with geospatial information.
    `UrbanMapper` steps support using multiple datasets. The user can create multiple loader instances, one for each dataset, 
    combine them in a single dictionary with suitable keys, and use it in your pipeline.
    Besides, geolocation can be loaded from latitude-longitude data columns or geometry specified in [WKT format](https://libgeos.org/specifications/wkt/).

    Meanwhile, we recommend to look through the [`Example`'s Loader](../copy_of_examples/1-Per-Module/1-loader/) for a more hands-on introduction about
    the Loader module and its usage.

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