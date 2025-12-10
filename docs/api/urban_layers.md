# Urban Layer

!!! tip "What is the Urban Layer's module?"
    The `urban_layer` module is responsible for the spatial canvases on which your datasets are displayed. These layers
    provide structure for urban insights, such as mapping taxi trips to busy `intersections` or analysing `neighbourhood`
    demographics.
    A dataset is projected over an `urban_layer` based on latitude-longitude data columns or geometry specified in [WKT format](https://libgeos.org/specifications/wkt/).    

    Meanwhile, we recommend to look through the [`Example`'s Urban layer](../copy_of_examples/1-Per-Module/2-urban_layer/) for a more hands-on introduction about
    the Urban layer module and its usage.

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.urban_layer.UrbanLayerBase
    options:
        heading: "UrbanLayerBase"
        members:
            - from_place 
            - from_file 
            - _map_nearest_layer
            - map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.OSMNXStreets
    options:
        heading: "Streets Roads"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_xml
            - from_file
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.OSMNXIntersections
    options:
        heading: "Streets Intersections"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_xml
            - from_file
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.OSMFeatures
    options:
        heading: "Streets Fatures"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_file
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.Tile2NetSidewalks
    options:
        heading: "Streets Fatures"
        members:
            - from_file
            - from_place
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.Tile2NetCrosswalks
    options:
        heading: "Streets Fatures"
        members:
            - from_file
            - from_place
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.RegionNeighborhoods
    options:
        heading: "Region Neighborhoods"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_file
            - infet_best_admin_level
            - _calculate_connectivity
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.RegionCities
    options:
        heading: "Region Cities"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_file
            - infet_best_admin_level
            - _calculate_connectivity
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.RegionStates
    options:
        heading: "Region States"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_file
            - infet_best_admin_level
            - _calculate_connectivity
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.RegionCountries
    options:
        heading: "Region Countries"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_file
            - infet_best_admin_level
            - _calculate_connectivity
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.CustomUrbanLayer
    options:
        heading: "CustomUrbanLayer"
        members:
            - from_file 
            - from_urban_layer
            - from_place
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview

## ::: urban_mapper.modules.urban_layer.UrbanLayerFactory
    options:
        heading: "LoaderFactory"
        members:
            - with_type 
            - with_mapping
            - build
            - preview
            - with_preview

## ::: urban_mapper.modules.urban_layer.AdminFeatures
    options:
        heading: "AdminFeatures"
        members:
            - load 
            - features

## ::: urban_mapper.modules.urban_layer.AdminRegions
    options:
        heading: "AdminRegions"
        members:
            - from_place
            - from_address
            - from_bbox
            - from_point
            - from_polygon
            - from_file
            - infet_best_admin_level
            - _calculate_connectivity
            - _map_nearest_layer
            - get_layer
            - get_layer_bounding_box
            - static_render
            - preview